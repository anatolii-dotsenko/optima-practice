# `GET /api/v1/orders/admin`

**Purpose.** Retrieve all customer orders across the system for barista queue processing and order fulfillment monitoring (requires administrative privileges per ADR-0008).

**Authentication.** Admin Bearer token (`Authorization: Bearer <token>`)

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `status` | query | string | no | Filter by lifecycle status: `pending`, `confirmed`, `ready`, `completed`, `cancelled` |
| `limit` | query | integer | no | Maximum orders to return (default: 100, max: 200) |
| `offset` | query | integer | no | Pagination offset (default: 0) |

## Request Example

```http
GET /api/v1/orders/admin?status=pending HTTP/1.1
Host: localhost:8000
Authorization: Bearer <admin_token>
```

## Successful Response

`200 OK`

```json
[
  {
    "id": 1,
    "user_id": 4,
    "status": "pending",
    "total_amount": "205.00",
    "notes": "Будь ласка, на вівсяному молоці",
    "created_at": "2026-09-12T13:45:00Z",
    "customer_email": "customer1@optima.ua",
    "customer_name": "Іван Коваленко",
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
]
```

## Error Responses

### 403 Forbidden (Non-admin user)
```json
{
  "code": "forbidden",
  "message": "Admin privileges required for this operation",
  "details": null
}
```
