# ADR-0008: Role-Based Access Control and Administrative Boundaries

- **Status:** Accepted
- **Date:** 2026-09-12
- **Deciders:** Development Team
- **Related requirements:** FR-08 (Menu Management), FR-09 (Staff Order Dashboard), NFR-02 (Security & Access Control)

## Context

The coffee shop online ordering system serves two distinct user personas:
1. **Customers:** Browse public catalog items, assemble shopping carts, place pre-orders, and monitor their own order history.
2. **Staff / Administrators:** Maintain the catalog (adding/editing items, adjusting prices, toggling stop-list availability, organizing categories) and process the incoming kitchen order queue (viewing all active orders across all customers, transitioning preparation states).

Without authorization boundaries at the API layer, regular customers could manipulate catalog prices, archive categories, or intercept private order details belonging to other users.

## Decision

We enforce **Role-Based Access Control (RBAC)** at the HTTP and dependency injection layer using a dedicated FastAPI dependency `get_current_admin_user`:

1. **User Role Representation:** The `User` model retains an explicit `is_superuser` boolean flag. This attribute is serialized into `UserResponse` DTOs to allow clients to render administrative controls conditionally.
2. **Authoritative Dependency Gate:** Endpoints performing catalog mutations (`POST /api/v1/menu/items`, `PUT /api/v1/menu/items/{id}`, `PATCH /api/v1/menu/items/{id}/availability`, `DELETE /api/v1/menu/items/{id}`, `POST/PUT/DELETE /api/v1/menu/categories`) and kitchen order queue retrieval (`GET /api/v1/orders/admin`) inject `get_current_admin_user`.
3. **Rejection Semantics:** If an unauthenticated user calls an administrative endpoint, HTTP 401 Unauthorized is returned. If an authenticated user lacks `is_superuser == True`, HTTP 403 Forbidden is returned with machine-readable code `"forbidden"`.
4. **Client-Side Progressive Disclosure:** The client UI fetches the authenticated user profile via `/api/v1/auth/me`. If `is_superuser` is true, the `⚙️ Адмінка` navigation item is mounted. Attempting to navigate directly to `#/admin` while unauthorized triggers a redirection or access-denied state.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| **ORM Flag + Dependency Gate (Chosen)** | Simple, immediate revocation upon flag change in DB, no token staleness, explicit 403 status codes. | Requires database user lookup per request (already standard in session middleware). | **Chosen** for strong consistency and simplicity within a 3-tier monolithic service. |
| **JWT Scopes / Claims Only** | Stateless token verification without database lookup. | Role changes or suspensions require waiting for token expiry or implementing complex token revocation blacklists. | Token staleness risk during staff role changes. |
| **Separate Admin Microservice / Port** | Physical network isolation of administrative endpoints. | High architectural overhead, duplicated models/schemas, complex deployment topology for a coffee shop MVP. | Excessive complexity disproportionate to system scale. |
| **Client-Side UI Hiding Only** | Trivial implementation. | Zero security: endpoints remain open to raw curl or HTTP client tampering. | Rejected as an unacceptable security failure. |

## Consequences

**Positive**
- Administrative mutations are guaranteed safe from customer-side tampering.
- Clear separation between public customer endpoints and staff operational endpoints.
- Integration tests can cleanly assert both 403 Forbidden and 200/201 Success behaviors.

**Negative**
- Every administrative route must explicitly declare `get_current_admin_user` dependency.

**Risks and mitigation**
- *Accidental exposure of a newly added admin route* → Automated tests enforce 403 assertions on all administrative paths with standard user headers.

## Verification

- Automated integration tests in `test_menu_api.py` and `test_orders_api.py` confirming 403 Forbidden for regular users and 200/201 Success for admin users.
- Live verification logging in with configured administrator credentials (`FIRST_SUPERUSER_EMAIL` / `FIRST_SUPERUSER_PASSWORD`) vs regular customer accounts.
