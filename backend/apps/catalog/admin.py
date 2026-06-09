from django.contrib import admin

from apps.catalog.models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ["name", "vcpu", "ram_mb", "disk_gb", "monthly_price", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
