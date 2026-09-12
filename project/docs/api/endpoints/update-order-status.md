# `PATCH /api/v1/orders/{id}/status`

**Purpose.** Transition the status of an existing order per the order state machine rules (ADR-0006).

**Authentication.** Bearer token (`Authorization: Bearer <token>`)

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `id` | path | integer | yes | ID of the order to update |
| `status` | body | string | yes | Target status: `pending`, `confirmed`, `ready`, `completed`, `cancelled` |

## State Transition Matrix (ADR-0006)

| Current Status | Allowed Next Statuses |
|---|---|
| `pending` | `confirmed`, `cancelled` |
| `confirmed` | `ready`, `cancelled` |
| `ready` | `completed`, `cancelled` |
| `completed` | *(Terminal state)* |
| `cancelled` | *(Terminal state)* |

## Request

```http
PATCH /api/v1/orders/1/status HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

```json
{
  "status": "confirmed"
}
```

## Successful response

`200 OK`

```json
{
  "id": 1,
  "user_id": 4,
  "status": "confirmed",
  "total_amount": "205.00",
  "notes": "Будь ласка, на вівсяному молоці",
  "created_at": "2026-09-12T13:45:00Z",
  "items": [
    {
      "id": 1,
      "menu_item_id": 2,
      "item_name": "Капучино Класичний",
      "unit_price": "70.00",
      "quantity": 2
    }
  ]
}
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 400 | `invalid_state_transition` | Attempted invalid transition (e.g. `confirmed` to `completed`) | Check current order status and only trigger valid transitions |
| 401 | `unauthorized` | Missing or invalid Bearer token | Prompt user to log in |
| 404 | `order_not_found` | Order ID does not exist | Verify order ID |
| 422 | `validation_failed` | Unrecognized status enum string | Provide one of the supported status enum values |

```json
{
  "code": "invalid_state_transition",
  "message": "Cannot transition order from 'confirmed' to 'completed'",
  "details": { "current_status": "confirmed", "target_status": "completed" }
}
```

## Notes

- Idempotent: transitions are deterministic; re-applying the same status is rejected as an invalid transition once executed.
- Related ADR: [ADR-0006: Order State Machine and Lifecycle](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/0006-order-state-machine-and-lifecycle.md)
