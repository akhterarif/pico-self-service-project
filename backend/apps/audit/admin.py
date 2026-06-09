from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "customer", "entity_type", "entity_id", "action"]
    list_filter = ["action", "entity_type"]
    search_fields = ["description", "entity_id"]
