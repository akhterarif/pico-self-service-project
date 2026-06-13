from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.services import AuditService
from apps.billing.models import Invoice, InvoiceStatus
from apps.compute.models import VirtualMachine
from services.payments.mock_gateway import MockPaymentGateway


class InvoiceService:
    @staticmethod
    def generate_for_vm(vm: VirtualMachine) -> Invoice:
        number = f"INV-{timezone.now():%Y%m%d}-{vm.id:06d}"

        period_start = vm.next_billing_date 
        period_end = vm.next_billing_date + relativedelta(months=1)

        invoice, created = Invoice.objects.get_or_create(
            invoice_number=number,
            defaults={
                "customer": vm.customer,
                "vm": vm,
                "amount": vm.package.monthly_price,
                "currency": "USD",
                "due_date": timezone.localdate() + relativedelta(days=14),
                "billing_period_start": period_start,
                "billing_period_end": period_end,
            },
        )
        vm.next_billing_date += relativedelta(months=1)
        vm.save(update_fields=["next_billing_date"])
        if created:
            AuditService.record(
                customer=vm.customer,
                entity_type="invoice",
                entity_id=invoice.id,
                action="INVOICE_GENERATED",
                description=f"Invoice {invoice.invoice_number} generated for {vm.name}.",
                metadata={"amount": str(invoice.amount), "vm_id": vm.id},
            )
        return invoice

    def get_unpaid_invoices() -> list[Invoice]:
        # TODO: Add another table to track upcoming due invoices instead of doing this query every time
        return list(Invoice.objects.filter(status=InvoiceStatus.PENDING, due_date__lte=timezone.localdate() + relativedelta(days=3)))
    
    def get_expired_pending_invoices() -> list[Invoice]:
        # TODO: Add another table to track expired pending invoices instead of doing this query every time
        return list(Invoice.objects.filter(status=InvoiceStatus.PENDING, due_date__lt=timezone.localdate()))
    
    def get_overdue_invoices() -> list[Invoice]:
        # TODO: Add another table to track overdue invoices instead of doing this query every time
        return list(Invoice.objects.filter(status=InvoiceStatus.OVERDUE, due_date__lt=timezone.localdate()))

class InvoicePaymentService:
    def __init__(self, gateway: MockPaymentGateway | None = None) -> None:
        self.gateway = gateway or MockPaymentGateway()

    @transaction.atomic
    def pay(self, *, invoice: Invoice, actor_customer) -> Invoice:
        if invoice.customer_id != actor_customer.id:
            raise PermissionError("Invoice does not belong to customer.")
        if invoice.status == InvoiceStatus.PAID:
            return invoice
        result = self.gateway.charge(invoice)
        if result.status != "SUCCESS":
            raise RuntimeError("Payment failed.")
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=["status", "paid_at"])
        AuditService.record(
            customer=invoice.customer,
            entity_type="invoice",
            entity_id=invoice.id,
            action="INVOICE_PAID",
            description=f"Invoice {invoice.invoice_number} paid.",
            metadata={"transaction_id": result.transaction_id},
        )
        return invoice
