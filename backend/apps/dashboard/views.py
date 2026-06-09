from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common import IsAdminRole, is_admin
from apps.dashboard.services import AdminDashboardService, CustomerDashboardService


class CustomerDashboardView(APIView):
    def get(self, request):
        if is_admin(request.user):
            return Response(AdminDashboardService.metrics())
        return Response(CustomerDashboardService.metrics(request.user.customer))


class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(AdminDashboardService.metrics())
