# PICO Self-Service Cloud Portal

PICO is a production-style MVP for a cloud self-service portal. Customers can register, browse VM packages, provision virtual machines, view invoices, pay bills, and inspect audit history. Admin users can view customer, resource, billing, and platform metrics.

## Architecture

- Backend: Django 5, Django REST Framework, SimpleJWT, Celery, Redis, PostgreSQL.
- Frontend: React, TypeScript, Vite, React Router, TanStack Query, Axios, TailwindCSS.
- Domain logic: service layer under backend apps and provider/payment abstractions under `backend/services`.
- Deployment: Docker Compose with postgres, redis, backend, celery, and frontend services.

## Technology Choices

Django and DRF provide strong auth, admin, ORM, and API primitives. Celery models async provisioning without binding the domain to a cloud vendor. React Query keeps frontend data fetching explicit and cache-aware. Docker Compose gives reviewers a single command development experience.

## Domain Model

Customers wrap Django users and are assigned `CUSTOMER` or `ADMIN` groups. Packages define VM sizes. Virtual machines belong to customers and carry a lifecycle state. Invoices belong to customers and optionally VMs. Audit logs capture customer-scoped and platform events with metadata.

## API Design

Swagger UI is available at `http://localhost:8000/api/docs/`.

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`
- `GET /api/packages/`
- `POST /api/vms/`, `GET /api/vms/`, `GET /api/vms/{id}/`
- `POST /api/vms/{id}/start`, `POST /api/vms/{id}/stop`, `DELETE /api/vms/{id}/`
- `GET /api/invoices/`, `POST /api/invoices/{id}/pay`
- `GET /api/audit/`
- `GET /api/dashboard/`
- `GET /api/admin/dashboard/`

## Provisioning Workflow

`VmProvisioningService` creates a VM as `REQUESTED`, calls the `CloudProvider` abstraction, moves it to `PROVISIONING`, writes audit logs, and dispatches a Celery task. The task simulates cloud completion, activates the VM, assigns IP data from the provider, writes audit logs, and generates the first invoice.

## Billing Workflow

Invoices are generated from provisioned VMs. `InvoicePaymentService` charges through `MockPaymentGateway`, marks the invoice `PAID`, records `paid_at`, and writes an audit event.

## Security Model

SimpleJWT protects APIs. Customers are restricted through querysets, object lookups, service ownership checks, and permissions. Admin group members can view all resources and platform metrics. Customer users only see their own VMs, invoices, audit logs, and dashboard.

## How To Run

```bash
docker compose up --build
```

Then open:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000/api/`
- Swagger: `http://localhost:8000/api/docs/`

Seed data is loaded automatically by the backend entrypoint after migrations.

## Demo Credentials

- Admin: `admin@example.com` / `password123`
- Customer: `customer@example.com` / `password123`

## Testing

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Future Improvements

- Real OpenStack integration
- Terraform integration
- Usage metering
- Network allocation
- Object storage
- Role based billing
- Payment providers

## AI Usage Disclosure

This assessment project was generated with AI assistance. Engineering choices, structure, and implementation were reviewed and organized to demonstrate maintainable full-stack design.
