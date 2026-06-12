import time

from celery import shared_task
from django.conf import settings

from apps.audit.services import AuditService
from apps.billing.services import InvoiceService
from apps.compute.models import VirtualMachine, VmStatus
from services.cloud.fake_openstack import FakeOpenStackProvider


@shared_task
def send_unpaid_invoice_notification() -> None:
    # Implementation for sending unpaid invoice notifications
    pass
    AuditService.record(
        customer=vm.customer,
        entity_type="vm",
        entity_id=vm.id,
        action="VM_ACTIVE",
        description=f"VM {vm.name} is active.",
        metadata={"ip_address": vm.ip_address},
    )
    InvoiceService.generate_for_vm(vm)


