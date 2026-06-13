from datetime import timedelta
from decimal import Decimal
import uuid

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Customer, Role
from apps.audit.services import AuditService
from apps.billing.models import Invoice, InvoiceStatus
from apps.catalog.models import Package
from apps.compute.models import VirtualMachine, VmStatus


class Command(BaseCommand):
    help = "Seed demo users, packages, VMs, invoices, and audit logs."

    def handle(self, *args, **options):
        customer_group, _ = Group.objects.get_or_create(name=Role.CUSTOMER)
        admin_group, _ = Group.objects.get_or_create(name=Role.ADMIN)

        admin, _ = User.objects.get_or_create(username="admin@example.com", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True})
        admin.set_password("password123")
        admin.is_staff = True
        admin.is_superuser = True
        admin.email = "admin@example.com"
        admin.save()
        admin.groups.add(admin_group)

        user, _ = User.objects.get_or_create(username="customer@example.com", defaults={"email": "customer@example.com"})
        user.set_password("password123")
        user.email = "customer@example.com"
        user.save()
        user.groups.add(customer_group)
        customer, _ = Customer.objects.get_or_create(user=user, defaults={"company_name": "Acme Cloud Labs"})

        packages = [
            ("Small", "small", 2, 4096, 50, Decimal("20.00")),
            ("Medium", "medium", 4, 8192, 100, Decimal("40.00")),
            ("Large", "large", 8, 16384, 200, Decimal("80.00")),
        ]
        package_objs = []
        for name, slug, vcpu, ram, disk, price in packages:
            package, _ = Package.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "vcpu": vcpu, "ram_mb": ram, "disk_gb": disk, "monthly_price": price, "is_active": True},
            )
            package_objs.append(package)

        for index in range(1, 6):
            vm, created = VirtualMachine.objects.get_or_create(
                customer=customer,
                name=f"demo-vm-{index}",
                defaults={
                    "package": package_objs[index % 3],
                    "cloud_server_id": str(uuid.uuid4()),
                    "status": VmStatus.ACTIVE,
                    "ip_address": f"10.42.0.{20 + index}",
                    "next_billing_date": timezone.now().date(),
                },
            )
            if created:
                AuditService.record(customer=customer, entity_type="vm", entity_id=vm.id, action="VM_ACTIVE", description=f"{vm.name} is active.")

        vms = list(VirtualMachine.objects.filter(customer=customer).order_by("id")[:3])
        for idx, vm in enumerate(vms, start=1):
            status = InvoiceStatus.PAID if idx == 1 else InvoiceStatus.PENDING
            invoice, _ = Invoice.objects.get_or_create(
                invoice_number=f"INV-DEMO-{idx:03d}",
                defaults={
                    "customer": customer,
                    "vm": vm,
                    "amount": vm.package.monthly_price,
                    "currency": "USD",
                    "status": status,
                    "due_date": timezone.localdate() + timedelta(days=14),
                    "paid_at": timezone.now() if status == InvoiceStatus.PAID else None,
                },
            )
            AuditService.record(customer=customer, entity_type="invoice", entity_id=invoice.id, action="INVOICE_GENERATED", description=f"{invoice.invoice_number} generated.")

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
