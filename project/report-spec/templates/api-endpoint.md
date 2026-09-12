# `{METHOD} /api/v1/{resource}`

**Purpose.** {One sentence: what this endpoint does and for whom.}

**Authentication.** {none | Bearer token | API key} — `Authorization: Bearer <token>`

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `{id}` | path | integer | yes | {what it identifies} |
| `{limit}` | query | integer | no | Page size, default 20, max 100 |
| `{field}` | body | string | yes | {constraints: length, format, allowed values} |

## Request

```http
POST /api/v1/{resource} HTTP/1.1
Host: {base_url}
Content-Type: application/json
Authorization: Bearer <token>
```

```json
{
  "field": "value"
}
```

## Successful response

`201 Created`

```json
{
  "id": 1,
  "field": "value",
  "created_at": "2026-01-01T10:00:00Z"
}
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 400 | `invalid_request` | Malformed body | Fix the payload |
| 401 | `unauthorized` | Missing or expired token | Re-authenticate |
| 404 | `not_found` | Resource does not exist | Show an empty state |
| 409 | `conflict` | Duplicate unique field | Ask the user for another value |
| 422 | `validation_failed` | Field constraints violated | Highlight the invalid fields |

```json
{
  "code": "validation_failed",
  "message": "Field 'email' has an invalid format",
  "details": { "field": "email" }
}
```

## Notes

- Rate limit: {N requests / minute}
- Idempotent: {yes | no}
- Related endpoints: {links}
