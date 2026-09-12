# ADR-0003: Deferring Secondary Go Edge Service

- **Status:** accepted
- **Date:** 2026-09-12
- **Deciders:** Engineering Team
- **Related requirements:** NFR-06 (Operational Simplicity), NFR-07 (Development Velocity)

## Context

`project-context.yaml` and `engineering-plan.yaml` note Go as a candidate secondary language for an edge service (reverse proxy, static file serving, rate limiting, or WebSocket gateway). However, `engineering-plan.yaml` explicitly states:
> *"A polyglot backend must be justified by a concrete non-functional requirement (throughput, latency, static binary size). Otherwise document it as a rejected alternative — an unjustified second language is a defensible-review risk."*

During Sprint 1, our primary focus is repository scaffolding, domain modeling, and robust authentication workflows.

## Decision

We will **defer and reject** the introduction of a secondary Go edge service for the current architecture.

Reverse proxying, CORS handling, and static file delivery can be adequately managed using standard containerized ingress (e.g. lightweight Nginx or direct ASGI hosting behind Podman network isolation), avoiding unnecessary polyglot complexity.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Single Language (Python/FastAPI) | Single toolchain, unified CI/CD, shared models/utilities, lower mental context switching | Higher memory footprint than static Go binary for raw proxying | **Chosen.** Meets all current throughput and latency requirements without introducing multiple build environments. |
| Polyglot Backend (FastAPI + Go Edge Service) | Static binary, minimal container footprint, high concurrency for edge proxying | Dual build toolchains, complex local setup, two language ecosystems to maintain in CI, difficult review defense | Rejected because current traffic projections do not exhibit extreme concurrency demands justifying a dedicated edge proxy. |

## Consequences

**Positive**
- Streamlined developer experience and simpler container builds.
- CI pipeline only needs to lint, test, and package Python and standard web assets.
- Elimination of review risks regarding unwarranted architectural complexity.

**Negative**
- If specialized high-throughput WebSocket routing or microsecond edge rate-limiting is required later, it must be introduced at that future point.

**Risks and mitigation**
- *Risk:* Future high concurrency requirements might outgrow single-tier ASGI hosting.
- *Mitigation:* The three-tier boundary preserves the ability to place a Go or Envoy reverse proxy in front of the API without altering backend domain code.

## Verification

Verified by demonstrating that FastAPI meets all current response time budgets (< 100ms for auth endpoints) and that the single-language pipeline simplifies CI and deployment configurations.
