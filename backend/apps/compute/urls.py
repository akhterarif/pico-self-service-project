from rest_framework.routers import DefaultRouter

from apps.compute.views import VmViewSet

router = DefaultRouter()
router.register("vms", VmViewSet, basename="vms")

urlpatterns = router.urls
