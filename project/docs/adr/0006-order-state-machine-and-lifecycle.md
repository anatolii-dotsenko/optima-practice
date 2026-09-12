# ADR-0006: Order State Machine and Lifecycle Management

- **Status:** Accepted
- **Date:** 2026-09-12
- **Author(s):** Development Team

## Context

The Coffee Shop Online Ordering system (Topic T2) requires reliable lifecycle tracking for pre-orders. When customers place pre-orders, the orders transition through several phases: placement, barista confirmation/preparation, readiness for pickup, fulfillment, or cancellation.

Without a well-defined and strictly enforced state machine:
1. Orders could jump into inconsistent or illegal states (e.g., from `COMPLETED` back to `PENDING`, or directly from `PENDING` to `COMPLETED` without kitchen confirmation).
2. Race conditions between customers cancelling and baristas completing drinks could result in resource waste or dispute.
3. Reporting and queue metrics (e.g. preparation time, active queue depth) would become inaccurate.

We need an explicit, deterministic state machine enforced in the domain service layer.

## Decision

We introduce an explicit, centralized state machine for all orders managed in `app.models.order.OrderStatus` and enforced inside `app.services.order_service.OrderService`.

### 1. State Definitions

- `PENDING`: Initial state upon pre-order creation. The order is registered in the database, pricing verified, waiting for barista intake.
- `CONFIRMED`: Barista has reviewed the order and begun coffee extraction/food preparation.
- `READY`: The items are prepared and waiting on the counter for customer pickup.
- `COMPLETED`: Customer picked up order (terminal success state).
- `CANCELLED`: Cancelled by customer (only allowed while `PENDING`) or by barista/admin due to out-of-stock or non-pickup (terminal cancellation state).

### 2. Legal Transition Matrix

| From State | Permitted Target States | Trigger Actor |
|---|---|---|
| `PENDING` | `CONFIRMED`, `CANCELLED` | Barista, Customer (cancellation) |
| `CONFIRMED` | `READY`, `CANCELLED` | Barista |
| `READY` | `COMPLETED`, `CANCELLED` | Barista, Cashier |
| `COMPLETED` | *None (Terminal)* | - |
| `CANCELLED` | *None (Terminal)* | - |

Any transition not explicitly listed above is rejected by raising `InvalidOrderStateError` (HTTP 400).

## Consequences

### Positive
- Strict auditability: Every order's progression is verifiable and deterministic.
- Clear separation of concerns: The business logic in `OrderService` enforces rules, shielding database integrity and presentation controllers.
- Front-end clarity: UI components can predictably disable/enable action buttons depending on the current status badge.

### Negative / Trade-offs
- Strict sequentiality means skipping states (e.g., instant complete without `READY`) is prohibited even for fast pickup, requiring explicit workflow actions.
