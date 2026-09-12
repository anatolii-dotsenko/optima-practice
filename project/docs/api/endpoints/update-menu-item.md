# `PUT /api/v1/menu/items/{item_id}`

**Purpose.** Update an existing menu item's details, such as title, description, price, category, photo URL, or availability (requires administrative privileges per ADR-0008).

**Authentication.** Admin Bearer token (`Authorization: Bearer <token>`)

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `item_id` | path | integer | yes | ID of the menu item to update |
| `name` | body | string | no | New display name (2–150 characters) |
| `description` | body | string | no | Updated description or ingredients |
| `price` | body | decimal | no | New price in ₴ (must be greater than 0) |
| `image_url` | body | string | no | New photo URL |
| `is_available` | body | boolean | no | Stock availability status |
| `category_id` | body | integer | no | Reassign to a different category ID |

## Request Example

```http
PUT /api/v1/menu/items/1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <admin_token>
Content-Type: application/json
```

```json
{
  "price": "55.00",
  "description": "Класичний італійський еспресо з оновленої фермерської Ефіопії"
}
```

## Successful Response

`200 OK`

```json
{
  "id": 1,
  "category_id": 1,
  "name": "Еспресо Класичний",
  "description": "Класичний італійський еспресо з оновленої фермерської Ефіопії",
  "price": "55.00",
  "image_url": "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=500&q=80",
  "is_available": true
}
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

### 404 Not Found
```json
{
  "code": "menu_item_not_found",
  "message": "Menu item 999 not found",
  "details": null
}
```
