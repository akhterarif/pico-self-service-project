import time

from celery import shared_task
from django.conf import settings

from apps.audit.services import AuditService
from apps.billing.services import InvoiceService
from apps.compute.models import VirtualMachine, VmStatus
from services.cloud.fake_openstack import FakeOpenStackProvider


@shared_task
def provision_vm(vm_id: int) -> None:
    vm = VirtualMachine.objects.select_related("customer", "package").get(id=vm_id)
    if vm.status != VmStatus.PROVISIONING:
        return
    if not settings.CELERY_TASK_ALWAYS_EAGER:
        time.sleep(3)
    server = FakeOpenStackProvider().get_server(vm.cloud_server_id)
    vm.status = VmStatus.ACTIVE
    vm.ip_address = server.ip_address
    vm.save(update_fields=["status", "ip_address", "updated_at"])
    AuditService.record(
        customer=vm.customer,
        entity_type="vm",
        entity_id=vm.id,
        action="VM_ACTIVE",
        description=f"VM {vm.name} is active.",
        metadata={"ip_address": vm.ip_address},
    )
    InvoiceService.generate_for_vm(vm)
