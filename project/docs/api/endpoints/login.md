# `POST /api/v1/auth/login`

**Purpose.** Authenticate user credentials and return a signed JSON Web Token (JWT) Bearer access token.

**Authentication.** none

## Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `email` | body | string | yes | Registered account email address |
| `password` | body | string | yes | Account password |

## Request

```http
POST /api/v1/auth/login HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "email": "customer@example.com",
  "password": "CoffeePassword123!"
}
```

## Successful response

`200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Error responses

| Status | `code` | When it happens | What the client should do |
|---|---|---|---|
| 401 | `unauthorized` | Email not found or password incorrect | Show invalid credentials message; allow retry |
| 403 | `forbidden` | Account is marked inactive | Display account suspension message |
| 422 | `validation_failed` | Payload fields are missing or invalid | Ensure email and password fields are filled |

```json
{
  "code": "unauthorized",
  "message": "Invalid email or password",
  "details": null
}
```

## Notes

- Token lifespan: 3600 seconds (60 minutes) by default
- Idempotent: no
- Related endpoints: [GET /api/v1/auth/me](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/me.md)
