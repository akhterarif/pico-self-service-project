from django.db import models

from apps.accounts.models import Customer
from apps.catalog.models import Package


class VmStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "Requested"
    PROVISIONING = "PROVISIONING", "Provisioning"
    ACTIVE = "ACTIVE", "Active"
    STOPPED = "STOPPED", "Stopped"
    ERROR = "ERROR", "Error"
    DELETED = "DELETED", "Deleted"


class VirtualMachine(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="vms")
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name="vms")
    name = models.CharField(max_length=120)
    cloud_server_id = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=VmStatus.choices, default=VmStatus.REQUESTED)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_billing_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
    
    @property
    def monthly_price(self):
        return self.package.monthly_price
