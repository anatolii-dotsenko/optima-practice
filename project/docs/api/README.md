# Coffee Shop Back-End API Reference

Comprehensive reference documentation for the Coffee Shop Online Ordering REST API.

## Overview

- **Purpose:** Exposes HTTP endpoints for customer authentication, user profile management, coffee ordering, and administration.
- **Base URL:** `http://localhost:8000/api/v1` (or configured via environment)
- **Data Format:** All request and response payloads are formatted in standard UTF-8 JSON (`Content-Type: application/json`).
- **Versioning:** URL prefix versioning (`/api/v1`).
- **Interactive Documentation:**
  - Swagger UI: `http://localhost:8000/api/v1/docs`
  - ReDoc: `http://localhost:8000/api/v1/redoc`
  - Raw OpenAPI 3.1: [openapi.yaml](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/openapi.yaml)

---

## Authentication

The API uses standard **JWT (JSON Web Token) Bearer Token Authentication**.

### How to Obtain a Token
1. Register an account via `POST /api/v1/auth/register`.
2. Authenticate with credentials via `POST /api/v1/auth/login`.
3. Receive JSON response containing `access_token` and `token_type: "bearer"`.

### Header Example
Include the token in the `Authorization` header on all protected requests:

```http
Authorization: Bearer <your_access_token>
```

---

## Endpoints Summary

| Method | Path | Summary | Auth | Detailed Documentation |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user | None | [register.md](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/register.md) |
| `POST` | `/api/v1/auth/login` | Authenticate & obtain JWT | None | [login.md](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/login.md) |
| `GET` | `/api/v1/auth/me` | Fetch authenticated profile | Bearer | [me.md](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/endpoints/me.md) |
| `GET` | `/health` | Liveness health check | None | Direct probe |

---

## Error Catalogue

All error responses strictly adhere to the standardized schema:

```json
{
  "code": "error_code_string",
  "message": "Human readable explanation of the failure",
  "details": { "optional": "contextual metadata" }
}
```

| HTTP Status | `code` | Meaning | What the Client Should Do |
|---|---|---|---|
| 400 | `domain_error` | Generic domain request failure | Inspect message and adjust input payload |
| 401 | `unauthorized` | Missing, invalid, or expired Bearer token / wrong login credentials | Prompt user to log in or supply valid Bearer credentials |
| 403 | `forbidden` | User account is inactive or lacks requisite permission | Display access restricted alert to the user |
| 404 | `not_found` | Requested resource or user identifier does not exist | Display empty state or not found notification |
| 409 | `conflict` | Unique resource conflict (e.g. email already in use) | Ask the user to choose another email or reset password |
| 422 | `validation_failed` | Pydantic payload validation constraint violation | Highlight invalid fields on client form |
| 500 | `internal_error` | Unhandled server error | Display retry message and contact support |

---

## Rate Limiting & Performance

- Current Sprint 1 MVP applies connection timeouts (30s) and standard ASGI concurrent worker scaling.
- Default pagination rule (for collection endpoints in subsequent sprints): limit-offset with `default_limit: 20`, `max_limit: 100`.
