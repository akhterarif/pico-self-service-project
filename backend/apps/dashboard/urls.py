from django.urls import path

from apps.dashboard.views import AdminDashboardView, CustomerDashboardView

urlpatterns = [
    path("dashboard/", CustomerDashboardView.as_view(), name="customer-dashboard"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
