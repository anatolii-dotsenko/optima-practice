# `DELETE /api/v1/menu/items/{item_id}`

**Purpose.** Remove a menu item from the catalog permanently (requires administrative privileges per ADR-0008).

**Authentication.** Admin Bearer token (`Authorization: Bearer <token>`)

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `item_id` | path | integer | yes | ID of the menu item to delete |

## Request Example

```http
DELETE /api/v1/menu/items/10 HTTP/1.1
Host: localhost:8000
Authorization: Bearer <admin_token>
```

## Successful Response

`204 No Content`

*(Empty response body)*

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
  "message": "Menu item 10 not found",
  "details": null
}
```
