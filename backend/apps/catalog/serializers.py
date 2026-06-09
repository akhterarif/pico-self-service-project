from rest_framework import serializers

from apps.catalog.models import Package


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["id", "name", "slug", "vcpu", "ram_mb", "disk_gb", "monthly_price", "is_active"]
