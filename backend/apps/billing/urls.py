from rest_framework.routers import DefaultRouter

from apps.billing.views import InvoiceViewSet

router = DefaultRouter()
router.register("invoices", InvoiceViewSet, basename="invoices")

urlpatterns = router.urls
