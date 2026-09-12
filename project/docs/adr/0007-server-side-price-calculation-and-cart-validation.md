# ADR-0007: Server-Side Price Calculation and Cart Validation

- **Status:** Accepted
- **Date:** 2026-09-12
- **Author(s):** Development Team

## Context

In an online ordering system, the client application (browser or mobile app) manages a local shopping cart that records selected items and their quantities. If the client were permitted to send item prices or order totals directly in the order creation payload, malicious actors could tamper with network requests to place orders at arbitrary or negative prices.

Furthermore, menu item prices and availability (out-of-stock items) change dynamically in the database. Relying on cached client-side prices risks selling products below current rates or accepting orders for sold-out ingredients.

## Decision

We enforce **strictly server-authoritative price calculation and availability validation**:

1. **Client Payload Limitation:** The order creation payload (`OrderCreateRequest`) contains ONLY:
   - Array of `{ menu_item_id: UUID/int, quantity: int (1..50) }`
   - Optional customer notes string (`notes`)
   The client is strictly prohibited from supplying unit prices, subtotals, or total amounts.

2. **Server-Side Price Lookup & Availability Verification:**
   Inside `OrderService.create_order()`:
   - Look up current item records from `MenuItemRepository` in a single query.
   - Verify every item exists; otherwise raise `MenuItemNotFoundError` (HTTP 404).
   - Verify `is_available == True` for each item; otherwise raise `MenuItemUnavailableError` (HTTP 400).
   - Compute `item_subtotal = item.price * quantity`.
   - Compute `total_amount = sum(item_subtotal)`.
   - Snapshot the exact `unit_price` at moment of purchase into `OrderItem.unit_price`.

## Consequences

### Positive
- Total protection against client-side cart tampering and price fraud.
- Historical audit accuracy: When catalog prices change in the future, past orders retain their historical purchased `unit_price`.
- Concurrency safety: Discontinued or out-of-stock items are blocked immediately before order commitment.

### Negative / Trade-offs
- Slight network round-trip overhead to fetch current pricing, which is negligible compared to the financial and data integrity guarantees.
