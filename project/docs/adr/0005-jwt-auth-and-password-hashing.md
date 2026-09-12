# ADR-0005: Authentication Strategy using JWT and Modern Password Hashing

- **Status:** accepted
- **Date:** 2026-09-12
- **Deciders:** Engineering Team
- **Related requirements:** NFR-10 (Security), FR-03 (Authentication & Authorization)

## Context

User authentication is a foundational requirement for the coffee shop ordering system. The system needs to support secure registration, credential verification, and authenticated access to private resources (user profile, order history).

Security rules in `engineering-plan.yaml` mandate:
- Passwords must be hashed using a modern KDF (bcrypt/argon2), never stored in plain text.
- Secrets must be injected via environment variables.
- Passwords and tokens must never appear in application log streams.
- Stateless scalability is desirable for REST clients and decoupled frontends.

## Decision

We will implement authentication using:
1. **Password Hashing:** Passwords hashed with **bcrypt** with salt rounds configured via security settings.
2. **Stateless Access Tokens:** **JSON Web Tokens (JWT)** signed using the HMAC-SHA256 (`HS256`) algorithm.
3. **Transport Protocol:** Standard HTTP `Authorization: Bearer <token>` header on protected endpoints (`/api/v1/auth/me`).
4. **Token Expiry:** Access tokens issued with a configurable TTL (default 60 minutes).
5. **Configuration Isolation:** `SECRET_KEY`, `ALGORITHM`, and token lifetime managed strictly via Pydantic `Settings` reading environment variables.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| JWT Bearer Tokens + bcrypt | Stateless verification, works seamlessly across web/mobile clients, no central session store bottleneck | Token revocation requires token blocklist if needed before expiration | **Chosen.** Optimal balance for REST APIs, enabling clean decoupling of client and backend. |
| Server-Side Sessions (Cookies/Redis) | Immediate revocation on server side, smaller cookie payload | Requires stateful session storage (Redis/DB) for every request, CSRF mitigation overhead | Rejected due to extra stateful infrastructure overhead for current phase. |
| Basic HTTP Auth per request | Simplest protocol | Sends credentials with every request, cannot represent scoped claims or clean expiration | Rejected as insecure and poor user experience for modern web applications. |

## Consequences

**Positive**
- Backend instances can verify user claims without querying the database for every single authorized request.
- Passwords stored securely against brute-force and dictionary attacks.
- Standardized Bearer token auth is supported by OpenAPI and API documentation tools out of the box.

**Negative**
- Access tokens cannot be revoked before their expiration without introducing a token blacklist cache.

**Risks and mitigation**
- *Risk:* Leaked secret key compromising token validity.
- *Mitigation:* `SECRET_KEY` is loaded from environment variables (`.env`), never hardcoded in git, and `.env` is excluded in `.gitignore`. Short token expiry (60m) limits exposure.

## Verification

Verified by automated unit tests validating password hashing and verification, token creation and claim extraction, rejection of expired/invalid signatures, and integration tests verifying 401 Unauthorized responses for invalid or missing tokens.
