# `GET /api/v1/menu/categories`

**Purpose.** Retrieve the list of active menu categories ordered by display order.

**Authentication.** none (public endpoint)

## Parameters

None.

## Request

```http
GET /api/v1/menu/categories HTTP/1.1
Host: localhost:8000
Accept: application/json
```

## Successful response

`200 OK`

```json
[
  {
    "id": 1,
    "name": "Кава",
    "slug": "coffee",
    "description": "Класичні та авторські кавові напої на основі свіжообсмаженої 100% арабіки",
    "display_order": 1,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Чай та напої",
    "slug": "tea-and-drinks",
    "description": "Листовий чай, матча лате та натуральні лимонади",
    "display_order": 2,
    "is_active": true
  }
]
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 500 | `internal_error` | Database connectivity failure | Show retry alert |

## Notes

- Cached: Client can cache category list locally for session duration.
- Idempotent: yes
- Related endpoints: [GET /api/v1/menu/items](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/get-menu.md)
