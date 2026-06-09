from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.compute.views import VmAuditTrailView, VmInvoiceView, VmViewSet

router = DefaultRouter()
router.register("vms", VmViewSet, basename="vms")

urlpatterns = [
    path("vms/<int:pk>/audit/", VmAuditTrailView.as_view(), name="vms-audit"),
    path("vms/<int:pk>/invoice/", VmInvoiceView.as_view(), name="vms-invoice"),
    *router.urls,
]
