from rest_framework import serializers

from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "customer", "entity_type", "entity_id", "action", "description", "metadata", "created_at"]
