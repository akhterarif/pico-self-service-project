from django.contrib import admin

from apps.compute.models import VirtualMachine


@admin.register(VirtualMachine)
class VirtualMachineAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "customer", "package", "status", "ip_address", "created_at"]
    list_filter = ["status", "package"]
    search_fields = ["name", "customer__company_name", "cloud_server_id"]
