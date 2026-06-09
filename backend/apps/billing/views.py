from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.billing.models import Invoice
from apps.billing.serializers import InvoiceSerializer
from apps.billing.services import InvoicePaymentService
from apps.common import is_admin


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        qs = Invoice.objects.select_related("customer", "vm")
        if is_admin(self.request.user):
            return qs
        return qs.filter(customer=self.request.user.customer)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        invoice = self.get_object()
        invoice = InvoicePaymentService().pay(invoice=invoice, actor_customer=invoice.customer if is_admin(request.user) else request.user.customer)
        return Response(InvoiceSerializer(invoice).data)
