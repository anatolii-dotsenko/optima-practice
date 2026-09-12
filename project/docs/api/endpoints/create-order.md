# `POST /api/v1/orders`

**Purpose.** Place a new coffee pre-order. Performs server-authoritative price calculation and validates menu item availability (per ADR-0007).

**Authentication.** Bearer token (`Authorization: Bearer <token>`)

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `items` | body | array | yes | List of order items (minimum 1 item) |
| `items[].menu_item_id` | body | integer | yes | ID of the selected menu item |
| `items[].quantity` | body | integer | yes | Quantity to order (1 to 50) |
| `notes` | body | string | no | Optional instructions for the barista (e.g., "oat milk") |

## Request

```http
POST /api/v1/orders HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

```json
{
  "items": [
    {
      "menu_item_id": 2,
      "quantity": 2
    },
    {
      "menu_item_id": 7,
      "quantity": 1
    }
  ],
  "notes": "Будь ласка, на вівсяному молоці"
}
```

## Successful response

`201 Created`

```json
{
  "id": 1,
  "user_id": 4,
  "status": "pending",
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
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 400 | `menu_item_unavailable` | One or more items in the cart are marked unavailable | Remove unavailable item from cart or prompt user |
| 401 | `unauthorized` | Missing or expired Bearer token | Prompt user to log in |
| 404 | `menu_item_not_found` | One of the item IDs does not exist in catalog | Remove item from cart and refresh catalog |
| 422 | `validation_failed` | Items array empty or quantity < 1 | Validate input constraints in cart UI |

```json
{
  "code": "menu_item_unavailable",
  "message": "Item 'Матча Лате' is currently not available for ordering",
  "details": { "menu_item_id": 5, "item_name": "Матча Лате" }
}
```

## Notes

- **Server-Authoritative Pricing (ADR-0007):** The client cannot submit or manipulate prices. Prices and subtotals are computed exclusively on the server using active database rates.
- **Initial Status:** Created orders enter state `pending` (ADR-0006).
- Idempotent: no
- Related endpoints: [GET /api/v1/orders](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/get-orders.md)
