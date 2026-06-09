from django.contrib import admin

from apps.billing.models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "customer", "vm", "amount", "currency", "status", "due_date", "paid_at"]
    list_filter = ["status", "currency"]
    search_fields = ["invoice_number", "customer__company_name"]
