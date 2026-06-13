import time

from celery import shared_task
from django.conf import settings

from apps.audit.services import AuditService
from apps.billing.services import InvoiceService
from apps.compute.models import VmStatus
from apps.compute.services import VmLifecycleService
from apps.billing.models import InvoiceStatus


@shared_task
def send_unpaid_invoice_notification() -> None:
    # Implementation for sending unpaid invoice notifications
    invoices = InvoiceService.get_unpaid_invoices()
    for invoice in invoices:
        # Here you would integrate with an email service to send the notification
        print(f"Sending unpaid invoice notification for Invoice {invoice.invoice_number} to Customer {invoice.customer.user.email}")

    AuditService.record(
        customer=invoice.customer,
        entity_type="invoice",
        entity_id=invoice.id,
        action="UNPAID_INVOICE_NOTIFICATION_SENT",
        description=f"Unpaid invoice notification sent for Invoice {invoice.invoice_number}.",
        metadata={"invoice_number": invoice.invoice_number},
    )

# TODO: Add a task to make invoice overdue if past due date and not paid, and then stop VMs with overdue invoices
@shared_task
def make_invoice_overdue() -> None:
    expired_pending_invoices = InvoiceService.get_expired_pending_invoices()
    for invoice in expired_pending_invoices:
        invoice.status = InvoiceStatus.OVERDUE
        invoice.save(update_fields=["status"])
        print(f"Invoice {invoice.invoice_number} is now overdue.")



@shared_task
def stop_overdue_vms() -> None:
    # Implementation for stopping VMs with overdue invoices
    overdue_invoices = InvoiceService.get_overdue_invoices()
    for invoice in overdue_invoices:
        vm = invoice.vm
        if vm and vm.status == VmStatus.ACTIVE:
            # Here you would integrate with the VM lifecycle service to stop the VM
            print(f"Stopping VM {vm.name} due to overdue Invoice {invoice.invoice_number}")
            VmLifecycleService().stop(vm=vm, actor_customer=None)

        # TODO: Add notification to customer about VM being stopped due to overdue invoice

        AuditService.record(
            customer=invoice.customer,
            entity_type="invoice",
            entity_id=invoice.id,
            action="OVERDUE_VM_STOPPED",
            description=f"VM {vm.name} stopped due to overdue Invoice {invoice.invoice_number}.",
            metadata={"invoice_number": invoice.invoice_number, "vm_id": vm.id},
        )
