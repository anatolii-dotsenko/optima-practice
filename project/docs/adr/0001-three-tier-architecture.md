# ADR-0001: Adoption of Three-Tier Architecture

- **Status:** accepted
- **Date:** 2026-09-12
- **Deciders:** Engineering Team
- **Related requirements:** NFR-01 (Modularity), NFR-02 (Maintainability), NFR-03 (Scalability)

## Context

The system being developed is an online coffee shop ordering platform (*Компанія 2 / T2*). The system must support customer ordering, cart management, status tracking, and an administrative interface for menu and order management.

The architectural design must ensure clean separation of concerns, allow independent evolution of the presentation layer and business logic, support testability of domain rules without spinning up web servers or databases, and fit within the team's rapid delivery constraints.

## Decision

We will adopt a **Three-Tier Architecture** consisting of:
1. **Presentation Tier (Client/Frontend):** Component-based client handling user interactions, presentation state, and consuming REST APIs.
2. **Logic Tier (Application/Backend Services):** Python/FastAPI service structured strictly by layered boundaries: API routing layer -> domain services -> data repositories.
3. **Data Tier (Persistence):** Relational database (PostgreSQL) handling relational integrity, transactions, and state storage.

Layer communication is strictly unidirectional (`Presentation -> API -> Services -> Repositories -> Database`). Services are decoupled from web framework concerns.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Three-Tier Architecture | Clear separation of concerns, testability, independent scaling of layers, well-defined boundaries | Slight overhead of DTO conversions and repository abstractions | **Chosen.** Optimal balance between delivery speed, maintainability, and academic defensibility. |
| Monolithic (Single-Layer/MVC) | Simplest initial setup, direct ORM access in controllers | High coupling, business logic leaks into views/controllers, hard to swap frontend or test in isolation | Rejected due to high coupling and violation of clean architectural layer rules. |
| Microservices Architecture | Granular independent deployments, fault isolation per service | High operational complexity, distributed transactions, elevated latency, excessive dev overhead for project scope | Rejected as premature optimization and disproportionate operational overhead for an MVP practice project. |

## Consequences

**Positive**
- Business rules in services can be thoroughly unit tested in isolation using repository fakes or mocks.
- Clear contract between API schemas (DTOs) and internal persistence models prevents accidental data leakage.
- Frontend and backend can be developed, tested, and containerized independently.

**Negative**
- Requires writing and maintaining DTO schemas, repository abstractions, and explicit mapping layers.

**Risks and mitigation**
- *Risk:* Developers might be tempted to skip layers (e.g. calling repositories directly from API routes or importing web request objects into services).
- *Mitigation:* Explicit layer rules enforced in `engineering-plan.yaml` and verified during code reviews and CI checks.

## Verification

Verified via architectural review, compliance with `engineering-plan.yaml` layer rules, and unit tests validating that domain services function without web framework dependencies.
