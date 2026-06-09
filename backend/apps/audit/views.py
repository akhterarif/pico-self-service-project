from rest_framework import generics

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.common import is_admin


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        qs = AuditLog.objects.select_related("customer")
        if is_admin(self.request.user):
            return qs
        return qs.filter(customer=self.request.user.customer)
