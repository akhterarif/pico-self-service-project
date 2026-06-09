from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import AdminCustomerListView, LoginView, MeView, RegisterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/register", RegisterView.as_view(), name="register"),
    path("api/auth/login", LoginView.as_view(), name="login"),
    path("api/auth/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me", MeView.as_view(), name="me"),
    path("api/admin/customers/", AdminCustomerListView.as_view(), name="admin-customers"),
    path("api/", include("apps.catalog.urls")),
    path("api/", include("apps.compute.urls")),
    path("api/", include("apps.billing.urls")),
    path("api/", include("apps.audit.urls")),
    path("api/", include("apps.dashboard.urls")),
]
