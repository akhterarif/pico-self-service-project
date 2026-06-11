from django.conf import settings
from django.db import models

from apps.accounts.models import Customer


class ChatStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_chats")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_chats")
    prompt = models.TextField()
    response = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ChatStatus.choices, default=ChatStatus.PENDING)
    error = models.TextField(blank=True)
    source_docs = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ChatMessage({self.user}, {self.status})"
