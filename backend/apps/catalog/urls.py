from rest_framework.routers import DefaultRouter

from apps.catalog.views import PackageViewSet

router = DefaultRouter()
router.register("packages", PackageViewSet, basename="packages")

urlpatterns = router.urls
