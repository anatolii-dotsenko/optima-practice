# ADR-0002: Selection of FastAPI for Backend Framework

- **Status:** accepted
- **Date:** 2026-09-12
- **Deciders:** Engineering Team
- **Related requirements:** NFR-04 (Performance), NFR-05 (Developer Ergonomics), FR-01 (API Standards)

## Context

The backend service is required to expose RESTful APIs, validate incoming payloads strictly, generate compliant OpenAPI specifications automatically, and integrate seamlessly with modern Python typing and ORM layers.

We evaluated the primary Python backend framework candidates specified in `project-context.yaml` and `engineering-plan.yaml`: FastAPI, Django, and Flask.

## Decision

We will use **FastAPI** on Python 3.12+ (compatible with Python 3.9+) as our primary backend framework.

FastAPI will be utilized strictly at the API transport layer (`backend/app/api/`) for routing, dependency injection, HTTP status mapping, and Pydantic validation. The domain services layer will remain independent of FastAPI imports.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| FastAPI | Native Pydantic integration, automatic OpenAPI 3.1 generation, async/await native support, high performance, strict typing | Lacks built-in ORM/admin panel (requires composing SQLAlchemy + Alembic) | **Chosen.** Best-in-class API validation, automatic OpenAPI doc generation, and clean separation between transport and business logic. |
| Django (with DRF) | Batteries-included, mature ORM, built-in admin panel | Heavy footprint, tightly coupled ORM, opinionated monolithic patterns making three-tier layer separation cumbersome | Rejected due to architectural weight, coupling to Django ORM, and slower execution compared to ASGI frameworks. |
| Flask | Minimalist, highly flexible, vast ecosystem | No native async, no native type validation, manual OpenAPI schema maintenance, requires multiple disparate third-party extensions | Rejected because automated validation and schema generation requires assembling disjoint plugins. |

## Consequences

**Positive**
- Automatic synchronization between Pydantic validation schemas and OpenAPI documentation.
- High request throughput and low latency on Starlette/Uvicorn foundation.
- Strong typing ergonomics and IDE autocompletion across schemas and dependency injection.

**Negative**
- Requires configuring database connections, sessions, and migrations manually with SQLAlchemy and Alembic.

**Risks and mitigation**
- *Risk:* FastAPI features (such as `HTTPException` or `Request`) could leak into service layers.
- *Mitigation:* Domain services will raise custom Python domain exceptions (`UserAlreadyExistsError`, `InvalidCredentialsError`), which are caught and converted to HTTP responses at the API layer or by custom exception handlers.

## Verification

Verified by automated OpenAPI schema generation matching the API documentation, strict Pydantic input validation, and successful execution of test suites with `pytest`.
