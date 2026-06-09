from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import Customer
from apps.accounts.serializers import CustomerSerializer, LoginSerializer, RegisterSerializer, UserSerializer
from apps.common import IsAdminRole


class RegisterView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=201)


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class AdminCustomerListView(ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.select_related("user").order_by("-created_at")
