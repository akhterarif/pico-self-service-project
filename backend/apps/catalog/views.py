from rest_framework import viewsets

from apps.catalog.models import Package
from apps.catalog.serializers import PackageSerializer


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PackageSerializer
    queryset = Package.objects.filter(is_active=True)
