from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Customer, Role
from apps.audit.services import AuditService


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    company_name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        group, _ = Group.objects.get_or_create(name=Role.CUSTOMER)
        user.groups.add(group)
        customer = Customer.objects.create(user=user, company_name=validated_data["company_name"])
        AuditService.record(
            customer=customer,
            entity_type="customer",
            entity_id=customer.id,
            action="CUSTOMER_REGISTERED",
            description=f"{customer.company_name} registered.",
        )
        return user

    def validate_email(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "role", "company_name"]

    def get_role(self, user: User) -> str:
        return Role.ADMIN if user.groups.filter(name=Role.ADMIN).exists() or user.is_staff else Role.CUSTOMER

    def get_company_name(self, user: User) -> str | None:
        return getattr(getattr(user, "customer", None), "company_name", None)


class CustomerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "email", "company_name", "created_at"]
