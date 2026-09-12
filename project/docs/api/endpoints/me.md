# `GET /api/v1/auth/me`

**Purpose.** Retrieve profile information for the currently authenticated user.

**Authentication.** Bearer token — `Authorization: Bearer <token>`

## Parameters

None (identity derived from the signed Bearer access token).

## Request

```http
GET /api/v1/auth/me HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Successful response

`200 OK`

```json
{
  "id": 1,
  "email": "customer@example.com",
  "full_name": "Oksana Petrenko",
  "is_active": true,
  "created_at": "2026-09-12T12:00:00Z"
}
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 401 | `unauthorized` | Token is missing, expired, or cryptographically invalid | Redirect user to the login screen |
| 403 | `forbidden` | User account has been deactivated | Inform user of account status |
| 404 | `not_found` | User record identified by token sub was deleted | Clear local token and re-register |

```json
{
  "code": "unauthorized",
  "message": "Invalid or expired access token",
  "details": null
}
```

## Notes

- Idempotent: yes
- Related endpoints: [POST /api/v1/auth/login](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/login.md)
