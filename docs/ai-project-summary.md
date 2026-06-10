# PICO Self-Service Project Summary

## Purpose
This repository implements a demo self-service cloud portal with:
- Django REST backend for authentication, VM provisioning, billing, audit, and dashboards
- React + TypeScript frontend with TailwindCSS, React Router, and TanStack Query
- Docker Compose for local development and a full-stack demo

## Backend Overview
- `backend/config/settings.py`: Django settings, JWT auth, CORS, Celery, Redis, database configuration
- `backend/config/urls.py`: API routing for authentication, catalog, compute, billing, audit, dashboard
- `backend/requirements.txt`: project dependencies including Django 5, DRF, SimpleJWT, Celery, Redis, PostgreSQL, pytest

### Apps
- `apps.accounts`: user registration/login, customer role, admin customer list
- `apps.catalog`: VM package catalog and package serializers
- `apps.compute`: VM model, provisioning and lifecycle services, VM API and viewset, VM audit/invoice endpoints
- `apps.billing`: invoice model, invoice listing, payment endpoint, billing service
- `apps.audit`: audit log model and list endpoint
- `apps.dashboard`: customer and admin dashboard metrics

### Domain Models
- `Customer`: extends Django `User` via one-to-one relation and stores `company_name`
- `Package`: VM offerings with CPU, RAM, disk, price, active flag
- `VirtualMachine`: owned by customer, tracks status, cloud server ID, IP address
- `Invoice`: linked to customer and VM, tracks amount, status, due date, paid timestamp
- `AuditLog`: event log with entity metadata

### Business Logic
- `VmProvisioningService`: creates a VM as `REQUESTED`, stores audit, calls provider, marks `PROVISIONING`, schedules Celery task
- `VmLifecycleService`: starts, stops, deletes VMs and validates ownership
- `InvoiceService`: generates invoices for provisioned VMs
- `InvoicePaymentService`: processes payments using `MockPaymentGateway`
- `AuditService`: centralized audit event creation
- `DashboardService`: widgets for customer and admin metrics

### External Abstractions
- `services/cloud/provider.py`: provider interface and `CloudServer` type
- `services/cloud/fake_openstack.py`: in-memory fake provider with server lifecycle simulation
- `services/payments/mock_gateway.py`: mock gateway that always succeeds

### Key API Endpoints
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`
- `GET /api/packages/`
- `GET /api/vms/`, `POST /api/vms/`, `DELETE /api/vms/{id}/`
- `POST /api/vms/{id}/start/`, `POST /api/vms/{id}/stop/`
- `GET /api/vms/{id}/audit/`, `GET /api/vms/{id}/invoice/`
- `GET /api/invoices/`, `POST /api/invoices/{id}/pay/`
- `GET /api/audit/`
- `GET /api/dashboard/`
- `GET /api/admin/dashboard/`
- `GET /api/admin/customers/`

### Auth / Security
- JWT authentication via SimpleJWT
- Admin users identified by `is_staff` or group `ADMIN`
- `apps.common.is_admin()` enforces admin access
- Customer access is restricted via queryset filtering and ownership checks

### Frontend Overview
- `frontend/src/api.ts`: Axios API client and typed request helpers
- `frontend/src/App.tsx`: routes for authenticated users and admin routes
- `frontend/src/components/AppLayout.tsx`: layout, navigation, auth guard, logout
- `frontend/src/hooks/useMe.ts`: current user query

### Frontend Routes
- `/login`, `/register`
- `/` Dashboard
- `/catalog` Catalog
- `/resources` Resources
- `/resources/:id` VM details
- `/invoices` Invoices
- `/audit` Audit logs
- `/profile` Profile
- `/admin`, `/admin/customers`, `/admin/resources`, `/admin/invoices`

### Run / Development Commands
- `docker compose up --build`
- Backend tests: `cd backend && pytest`
- Frontend tests: `cd frontend && npm test`
- Seed demo data: `python backend/manage.py seed_demo`

### Important Notes
- `CELERY_TASK_ALWAYS_EAGER` is enabled by default for local development, so Celery tasks execute synchronously.
- API base URL defaults to `http://localhost:8000/api`, configurable via `VITE_API_BASE_URL`.
- Swagger docs are available at `/api/docs/`.
- Demo credentials: `admin@example.com / password123`, `customer@example.com / password123`.
