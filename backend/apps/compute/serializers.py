from rest_framework import serializers

from apps.billing.models import Invoice
from apps.catalog.models import Package
from apps.catalog.serializers import PackageSerializer
from apps.compute.models import VirtualMachine
from services.cloud.fake_openstack import FakeOpenStackProvider


class VmSerializer(serializers.ModelSerializer):
    package = PackageSerializer(read_only=True)
    latest_invoice_id = serializers.SerializerMethodField()

    class Meta:
        model = VirtualMachine
        fields = ["id", "name", "package", "cloud_server_id", "status", "ip_address", "created_at", "updated_at", "latest_invoice_id"]

    def get_latest_invoice_id(self, vm: VirtualMachine) -> int | None:
        invoice = Invoice.objects.filter(vm=vm).order_by("-created_at").first()
        return invoice.id if invoice else None
    
class VmDetailSerializer(serializers.ModelSerializer):
    package = PackageSerializer(read_only=True)
    latest_invoice_id = serializers.SerializerMethodField()
    usage = serializers.SerializerMethodField(read_only=True, help_text="Current resource usage for the VM, e.g., CPU, RAM, Disk.")

    class Meta:
        model = VirtualMachine
        fields = ["id", "name", "package", "cloud_server_id", "status", "ip_address", "created_at", "updated_at", "latest_invoice_id", "usage"]

    def get_latest_invoice_id(self, vm: VirtualMachine) -> int | None:
        invoice = Invoice.objects.filter(vm=vm).order_by("-created_at").first()
        return invoice.id if invoice else None

    def get_usage(self, vm: VirtualMachine) -> dict[str, int]:
        usage = FakeOpenStackProvider().get_server_status(vm.cloud_server_id)
        return usage or {}


class VmCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    package_id = serializers.PrimaryKeyRelatedField(queryset=Package.objects.filter(is_active=True), source="package")
