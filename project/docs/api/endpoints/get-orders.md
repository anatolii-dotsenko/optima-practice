# `GET /api/v1/orders`

**Purpose.** Retrieve order history for the currently authenticated customer, sorted in reverse chronological order (newest first).

**Authentication.** Bearer token (`Authorization: Bearer <token>`)

## Parameters

None.

## Request

```http
GET /api/v1/orders HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

## Successful response

`200 OK`

```json
[
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
      },
      {
        "id": 2,
        "menu_item_id": 7,
        "item_name": "Круасан Вершковий Класичний",
        "unit_price": "65.00",
        "quantity": 1
      }
    ]
  }
]
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 401 | `unauthorized` | Bearer token is missing, expired, or malformed | Prompt user to log in again |

## Notes

- Strict isolation: Customers can only see their own orders. Staff and baristas will have role-filtered endpoints in Sprint 3.
- Idempotent: yes
- Related endpoints: [POST /api/v1/orders](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/create-order.md)
