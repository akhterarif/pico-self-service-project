from django.conf import settings
from django.db import transaction

from apps.audit.services import AuditService
from apps.catalog.models import Package
from apps.compute.models import VirtualMachine, VmStatus
from services.cloud.fake_openstack import FakeOpenStackProvider
from services.cloud.provider import CloudProvider


class VmProvisioningService:
    def __init__(self, provider: CloudProvider | None = None) -> None:
        self.provider = provider or FakeOpenStackProvider()

    @transaction.atomic
    def request_vm(self, *, customer, package: Package, name: str) -> VirtualMachine:
        vm = VirtualMachine.objects.create(customer=customer, package=package, name=name, status=VmStatus.REQUESTED)
        AuditService.record(
            customer=customer,
            entity_type="vm",
            entity_id=vm.id,
            action="VM_REQUESTED",
            description=f"VM {vm.name} requested.",
        )
        server = self.provider.create_server(
            name=name,
            vcpu=package.vcpu,
            ram_mb=package.ram_mb,
            disk_gb=package.disk_gb,
        )
        vm.cloud_server_id = server.server_id
        vm.status = VmStatus.PROVISIONING
        vm.save(update_fields=["cloud_server_id", "status", "updated_at"])
        AuditService.record(
            customer=customer,
            entity_type="vm",
            entity_id=vm.id,
            action="PROVISIONING_STARTED",
            description=f"Provisioning started for {vm.name}.",
            metadata={"cloud_server_id": server.server_id},
        )
        from apps.compute.tasks import provision_vm

        if settings.CELERY_TASK_ALWAYS_EAGER:
            provision_vm(vm.id)
        else:
            transaction.on_commit(lambda: provision_vm.delay(vm.id))
        return vm


class VmLifecycleService:
    def __init__(self, provider: CloudProvider | None = None) -> None:
        self.provider = provider or FakeOpenStackProvider()

    def start(self, *, vm: VirtualMachine, actor_customer) -> VirtualMachine:
        self._assert_owner(vm, actor_customer)
        self.provider.start_server(vm.cloud_server_id)
        vm.status = VmStatus.ACTIVE
        vm.save(update_fields=["status", "updated_at"])
        AuditService.record(customer=vm.customer, entity_type="vm", entity_id=vm.id, action="VM_STARTED", description=f"VM {vm.name} started.")
        return vm

    def stop(self, *, vm: VirtualMachine, actor_customer) -> VirtualMachine:
        self._assert_owner(vm, actor_customer)
        self.provider.stop_server(vm.cloud_server_id)
        vm.status = VmStatus.STOPPED
        vm.save(update_fields=["status", "updated_at"])
        AuditService.record(customer=vm.customer, entity_type="vm", entity_id=vm.id, action="VM_STOPPED", description=f"VM {vm.name} stopped.")
        return vm

    def delete(self, *, vm: VirtualMachine, actor_customer) -> VirtualMachine:
        self._assert_owner(vm, actor_customer)
        if vm.cloud_server_id:
            self.provider.delete_server(vm.cloud_server_id)
        vm.status = VmStatus.DELETED
        vm.save(update_fields=["status", "updated_at"])
        AuditService.record(customer=vm.customer, entity_type="vm", entity_id=vm.id, action="VM_DELETED", description=f"VM {vm.name} deleted.")
        return vm

    @staticmethod
    def _assert_owner(vm: VirtualMachine, actor_customer) -> None:
        if actor_customer and vm.customer_id != actor_customer.id:
            raise PermissionError("VM does not belong to customer.")
