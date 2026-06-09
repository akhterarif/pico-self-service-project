from decimal import Decimal

from django.db import models


class Package(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    vcpu = models.PositiveIntegerField()
    ram_mb = models.PositiveIntegerField()
    disk_gb = models.PositiveIntegerField()
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["monthly_price", "vcpu"]

    def __str__(self) -> str:
        return self.name
