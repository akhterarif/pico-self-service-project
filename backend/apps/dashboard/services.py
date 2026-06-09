from django.db.models import Sum

from apps.accounts.models import Customer
from apps.billing.models import Invoice, InvoiceStatus
from apps.compute.models import VirtualMachine, VmStatus


class CustomerDashboardService:
    @staticmethod
    def metrics(customer: Customer) -> dict:
        vms = VirtualMachine.objects.filter(customer=customer).exclude(status=VmStatus.DELETED)
        return {
            "total_vms": vms.count(),
            "active_vms": vms.filter(status=VmStatus.ACTIVE).count(),
            "pending_invoices": Invoice.objects.filter(customer=customer, status=InvoiceStatus.PENDING).count(),
            "monthly_cost": str(vms.aggregate(total=Sum("package__monthly_price"))["total"] or 0),
        }


class AdminDashboardService:
    @staticmethod
    def metrics() -> dict:
        return {
            "total_customers": Customer.objects.count(),
            "total_vms": VirtualMachine.objects.exclude(status=VmStatus.DELETED).count(),
            "active_vms": VirtualMachine.objects.filter(status=VmStatus.ACTIVE).count(),
            "total_revenue": str(Invoice.objects.filter(status=InvoiceStatus.PAID).aggregate(total=Sum("amount"))["total"] or 0),
            "pending_invoices": Invoice.objects.filter(status=InvoiceStatus.PENDING).count(),
        }
