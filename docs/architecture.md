# Architecture Notes

## Boundaries

The backend is organized by feature apps: accounts, catalog, compute, billing, audit, and dashboard. Cross-cutting external integrations live under `services/` so application workflows depend on contracts rather than concrete vendors.

## Clean Architecture in the MVP

Views authenticate, scope querysets, and call serializers/services. Serializers validate and shape data only. Business workflows live in service classes:

- `VmProvisioningService` coordinates VM request and provider creation.
- `VmLifecycleService` controls start, stop, and delete transitions.
- `InvoiceService` creates billing records.
- `InvoicePaymentService` coordinates mock payment and invoice state changes.
- `AuditService` centralizes audit creation.

## Cloud Provider Replacement

`CloudProvider` defines the required contract. `FakeOpenStackProvider` implements it for the assessment. A real `OpenStackProvider` can be added behind the same methods without changing provisioning or lifecycle services.

## Multi-Tenancy

Tenant isolation is enforced in viewset querysets and object retrieval. Customer dashboards, VM lists, invoices, and audit logs filter by `request.user.customer`. Admin users, identified by staff status or the `ADMIN` group, receive platform-wide querysets.

## Async Provisioning

Provisioning creates a database VM, calls the cloud provider, records audit events, and dispatches a Celery task on transaction commit. The task completes the simulated build, assigns IP data, records activation, and generates the initial invoice.

## Security Notes

The MVP uses JWT access and refresh tokens, role groups, object-scoped querysets, and service-level ownership checks. Production hardening would add refresh-token rotation, stricter CORS, HTTPS-only cookies or secure token storage, rate limiting, audit retention rules, and cloud credential secret management.
