# `POST /api/v1/auth/register`

**Purpose.** Register a new customer or staff user account with hashed password storage.

**Authentication.** none

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `email` | body | string | yes | Valid RFC 5322 email address (must be unique) |
| `password` | body | string | yes | Plain password, minimum 8 characters, letters and digits |
| `full_name` | body | string | yes | User's full name, 2–100 characters |

## Request

```http
POST /api/v1/auth/register HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "email": "customer@example.com",
  "password": "CoffeePassword123!",
  "full_name": "Oksana Petrenko"
}
```

## Successful response

`201 Created`

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
| 409 | `conflict` | The email address is already registered | Prompt the user to use a different email or log in |
| 422 | `validation_failed` | Email is invalid or password does not satisfy complexity requirements | Highlight the invalid fields with inline guidance |
| 500 | `internal_error` | Database connection error | Display a transient error notice |

```json
{
  "code": "conflict",
  "message": "User with email 'customer@example.com' already exists",
  "details": {
    "field": "email"
  }
}
```

## Notes

- Idempotent: no
- Related endpoints: [POST /api/v1/auth/login](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/login.md)
