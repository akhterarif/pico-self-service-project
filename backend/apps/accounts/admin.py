from django.contrib import admin

from apps.accounts.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "company_name", "user", "created_at"]
    search_fields = ["company_name", "user__email"]
