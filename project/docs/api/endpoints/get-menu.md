# `GET /api/v1/menu/items`

**Purpose.** Retrieve available menu items with optional category filtering and search query.

**Authentication.** none (public endpoint)

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `category_id` | query | integer | no | Filter items belonging to a specific category |
| `search` | query | string | no | Search items by title, description, or ingredients (case-insensitive) |

## Request

```http
GET /api/v1/menu/items?category_id=1&search=капучино HTTP/1.1
Host: localhost:8000
Accept: application/json
```

## Successful response

`200 OK`

```json
[
  {
    "id": 2,
    "category_id": 1,
    "name": "Капучино Класичний",
    "description": "Подвійний еспресо з шовковистою кремовою молочною пінкою, 250 мл",
    "price": "70.00",
    "image_url": "https://images.unsplash.com/photo-1534778101976-62847782c213?w=500&q=80",
    "is_available": true
  }
]
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 404 | `category_not_found` | Provided `category_id` does not exist | Refresh category list or remove category filter |
| 422 | `validation_failed` | Invalid parameter types | Ensure category_id is an integer |
| 500 | `internal_error` | Internal server or database error | Show generic retry message |

```json
{
  "code": "category_not_found",
  "message": "Category with ID 999999 not found",
  "details": { "category_id": 999999 }
}
```

## Notes

- Idempotent: yes
- Related endpoints: [GET /api/v1/menu/categories](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/get-categories.md), [POST /api/v1/orders](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/create-order.md)
