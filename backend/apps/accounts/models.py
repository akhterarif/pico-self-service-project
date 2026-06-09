from django.conf import settings
from django.db import models


class Role:
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer")
    company_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.company_name
