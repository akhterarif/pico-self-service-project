from apps.accounts.models import Customer
from apps.audit.models import AuditLog


class AuditService:
    @staticmethod
    def record(
        *,
        customer: Customer | None,
        entity_type: str,
        entity_id: str | int,
        action: str,
        description: str,
        metadata: dict | None = None,
    ) -> AuditLog:
        return AuditLog.objects.create(
            customer=customer,
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            description=description,
            metadata=metadata or {},
        )
