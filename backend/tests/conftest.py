import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIClient

from apps.accounts.models import Customer, Role
from apps.catalog.models import Package


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def roles(db):
    Group.objects.get_or_create(name=Role.CUSTOMER)
    Group.objects.get_or_create(name=Role.ADMIN)


@pytest.fixture
def package(db):
    return Package.objects.create(name="Small", slug="small", vcpu=2, ram_mb=4096, disk_gb=50, monthly_price="20.00")


@pytest.fixture
def customer_user(db, roles):
    user = User.objects.create_user(username="alice@example.com", email="alice@example.com", password="password123")
    user.groups.add(Group.objects.get(name=Role.CUSTOMER))
    Customer.objects.create(user=user, company_name="Alice Co")
    return user


@pytest.fixture
def other_user(db, roles):
    user = User.objects.create_user(username="bob@example.com", email="bob@example.com", password="password123")
    user.groups.add(Group.objects.get(name=Role.CUSTOMER))
    Customer.objects.create(user=user, company_name="Bob Co")
    return user


@pytest.fixture
def admin_user(db, roles):
    user = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="password123", is_staff=True)
    user.groups.add(Group.objects.get(name=Role.ADMIN))
    return user


def auth(client, user):
    client.force_authenticate(user=user)
    return client
