import pytest
from django.contrib.auth.models import User

from apps.audit.models import AuditLog
from apps.billing.models import Invoice, InvoiceStatus
from apps.compute.models import VirtualMachine, VmStatus
from tests.conftest import auth


@pytest.mark.django_db
def test_register_creates_customer_and_audit(api_client):
    response = api_client.post("/api/auth/register", {"email": "new@example.com", "password": "password123", "company_name": "New Co"}, format="json")
    assert response.status_code == 201
    user = User.objects.get(username="new@example.com")
    assert user.customer.company_name == "New Co"
    assert AuditLog.objects.filter(customer=user.customer, action="CUSTOMER_REGISTERED").exists()


@pytest.mark.django_db
def test_login_returns_tokens(api_client, customer_user):
    response = api_client.post("/api/auth/login", {"email": "alice@example.com", "password": "password123"}, format="json")
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_me_returns_role(api_client, customer_user):
    response = auth(api_client, customer_user).get("/api/auth/me")
    assert response.status_code == 200
    assert response.data["role"] == "CUSTOMER"


@pytest.mark.django_db
def test_packages_are_listed(api_client, customer_user, package):
    response = auth(api_client, customer_user).get("/api/packages/")
    assert response.status_code == 200
    assert response.data[0]["slug"] == "small"


@pytest.mark.django_db
def test_provision_vm_creates_active_vm_invoice_and_audits(api_client, customer_user, package, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    response = auth(api_client, customer_user).post("/api/vms/", {"name": "web-1", "package_id": package.id}, format="json")
    assert response.status_code == 201
    vm = VirtualMachine.objects.get(id=response.data["id"])
    assert vm.status == VmStatus.ACTIVE
    assert vm.ip_address
    assert Invoice.objects.filter(vm=vm, status=InvoiceStatus.PENDING).exists()
    assert AuditLog.objects.filter(customer=customer_user.customer, action="VM_ACTIVE").exists()


@pytest.mark.django_db
def test_customer_only_sees_own_vms(api_client, customer_user, other_user, package):
    mine = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="mine")
    VirtualMachine.objects.create(customer=other_user.customer, package=package, name="other")
    response = auth(api_client, customer_user).get("/api/vms/")
    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [mine.id]


@pytest.mark.django_db
def test_customer_cannot_retrieve_other_vm(api_client, customer_user, other_user, package):
    vm = VirtualMachine.objects.create(customer=other_user.customer, package=package, name="other")
    response = auth(api_client, customer_user).get(f"/api/vms/{vm.id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_stop_and_start_vm(api_client, customer_user, package):
    vm = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="vm", status=VmStatus.ACTIVE, cloud_server_id="server-1")
    client = auth(api_client, customer_user)
    stop = client.post(f"/api/vms/{vm.id}/stop/")
    assert stop.status_code == 200
    assert stop.data["status"] == VmStatus.STOPPED
    start = client.post(f"/api/vms/{vm.id}/start/")
    assert start.status_code == 200
    assert start.data["status"] == VmStatus.ACTIVE


@pytest.mark.django_db
def test_delete_vm_marks_deleted(api_client, customer_user, package):
    vm = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="vm", status=VmStatus.ACTIVE, cloud_server_id="server-1")
    response = auth(api_client, customer_user).delete(f"/api/vms/{vm.id}/")
    assert response.status_code == 204
    vm.refresh_from_db()
    assert vm.status == VmStatus.DELETED


@pytest.mark.django_db
def test_invoice_list_is_tenant_scoped(api_client, customer_user, other_user, package):
    vm1 = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="mine")
    vm2 = VirtualMachine.objects.create(customer=other_user.customer, package=package, name="other")
    mine = Invoice.objects.create(invoice_number="INV-1", customer=customer_user.customer, vm=vm1, amount="20.00", due_date="2030-01-01")
    Invoice.objects.create(invoice_number="INV-2", customer=other_user.customer, vm=vm2, amount="20.00", due_date="2030-01-01")
    response = auth(api_client, customer_user).get("/api/invoices/")
    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [mine.id]


@pytest.mark.django_db
def test_pay_invoice_marks_paid(api_client, customer_user, package):
    vm = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="vm")
    invoice = Invoice.objects.create(invoice_number="INV-PAY", customer=customer_user.customer, vm=vm, amount="20.00", due_date="2030-01-01")
    response = auth(api_client, customer_user).post(f"/api/invoices/{invoice.id}/pay/")
    assert response.status_code == 200
    invoice.refresh_from_db()
    assert invoice.status == InvoiceStatus.PAID
    assert invoice.paid_at is not None


@pytest.mark.django_db
def test_customer_cannot_pay_other_invoice(api_client, customer_user, other_user, package):
    vm = VirtualMachine.objects.create(customer=other_user.customer, package=package, name="other")
    invoice = Invoice.objects.create(invoice_number="INV-OTHER", customer=other_user.customer, vm=vm, amount="20.00", due_date="2030-01-01")
    response = auth(api_client, customer_user).post(f"/api/invoices/{invoice.id}/pay/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_audit_is_tenant_scoped(api_client, customer_user, other_user):
    AuditLog.objects.create(customer=customer_user.customer, entity_type="vm", entity_id="1", action="A", description="mine")
    AuditLog.objects.create(customer=other_user.customer, entity_type="vm", entity_id="2", action="B", description="other")
    response = auth(api_client, customer_user).get("/api/audit/")
    assert response.status_code == 200
    assert [item["description"] for item in response.data] == ["mine"]


@pytest.mark.django_db
def test_customer_dashboard_metrics(api_client, customer_user, package):
    vm = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="vm", status=VmStatus.ACTIVE)
    Invoice.objects.create(invoice_number="INV-DASH", customer=customer_user.customer, vm=vm, amount="20.00", due_date="2030-01-01")
    response = auth(api_client, customer_user).get("/api/dashboard/")
    assert response.status_code == 200
    assert response.data["total_vms"] == 1
    assert response.data["active_vms"] == 1
    assert response.data["pending_invoices"] == 1


@pytest.mark.django_db
def test_admin_can_use_root_dashboard_endpoint(api_client, admin_user, customer_user, package):
    vm = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="vm", status=VmStatus.ACTIVE)
    Invoice.objects.create(invoice_number="INV-ROOT-ADMIN", customer=customer_user.customer, vm=vm, amount="20.00", status=InvoiceStatus.PAID, due_date="2030-01-01")
    response = auth(api_client, admin_user).get("/api/dashboard/")
    assert response.status_code == 200
    assert response.data["total_customers"] == 1
    assert response.data["active_vms"] == 1
    assert response.data["total_revenue"] == "20"


@pytest.mark.django_db
def test_admin_dashboard_metrics(api_client, admin_user, customer_user, package):
    vm = VirtualMachine.objects.create(customer=customer_user.customer, package=package, name="vm", status=VmStatus.ACTIVE)
    Invoice.objects.create(invoice_number="INV-ADMIN", customer=customer_user.customer, vm=vm, amount="20.00", status=InvoiceStatus.PAID, due_date="2030-01-01")
    response = auth(api_client, admin_user).get("/api/admin/dashboard/")
    assert response.status_code == 200
    assert response.data["total_customers"] == 1
    assert response.data["active_vms"] == 1
    assert response.data["total_revenue"] == "20"


@pytest.mark.django_db
def test_non_admin_cannot_access_admin_dashboard(api_client, customer_user):
    response = auth(api_client, customer_user).get("/api/admin/dashboard/")
    assert response.status_code == 403
