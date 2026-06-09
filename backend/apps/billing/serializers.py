from rest_framework import serializers

from apps.billing.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    vm_name = serializers.CharField(source="vm.name", read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "vm", "vm_name", "amount", "currency", "status", "due_date", "created_at", "paid_at"]
