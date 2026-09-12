# ADR-0004: Selection of PostgreSQL and Persistence Strategy

- **Status:** accepted
- **Date:** 2026-09-12
- **Deciders:** Engineering Team
- **Related requirements:** NFR-08 (Data Integrity), NFR-09 (Data Persistence), FR-02 (User Accounts)

## Context

The system requires reliable storage for relational data, including customer profiles, menu items, orders, and payment records. The database must support ACID transactions, foreign key constraints, indexes on filtering columns, and containerized deployment with guaranteed persistence across container restarts.

In addition, automated testing requires fast, isolated test database execution without requiring a persistent external server.

## Decision

We will use **PostgreSQL 16** as the production and containerized database engine, managed via **SQLAlchemy 2.0** ORM and **Alembic** for schema migrations.

Key persistence strategies:
1. **Container Deployment:** Run PostgreSQL in a dedicated container managed by `podman-compose`.
2. **Named Volume Persistence:** Store data on a named volume (`pgdata:/var/lib/postgresql/data`) to guarantee data survives container recreation.
3. **Repository Abstraction:** All query logic is encapsulated inside repository classes (`backend/app/repositories/`).
4. **Testing Strategy:** SQLite in-memory database is supported for ultra-fast, dependency-free unit/integration test suites, while PostgreSQL is targeted for containerized runtime.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| PostgreSQL + SQLAlchemy 2.0 | Strong ACID compliance, rich SQL features, robust ecosystem, wide industry standard, supported by Alembic | Requires running a database service for full integration | **Chosen.** Meets all data integrity and transaction requirements. |
| MySQL / MariaDB | Broad hosting support, mature tooling | Less robust JSON support, subtle behavioral nuances with constraints compared to PostgreSQL | Rejected in favor of PostgreSQL's stricter constraint handling and standard features. |
| MongoDB (NoSQL) | Flexible document schema, fast write performance | Weak support for relational integrity across orders/customers, no native transactional foreign keys | Rejected because ordering, menus, and user credentials inherently require relational consistency. |

## Consequences

**Positive**
- Reliable transactional guarantees for orders and user registration.
- Schema changes are traceable and reproducible through Alembic migration scripts.
- Data persists safely across container updates thanks to the named volume `pgdata`.

**Negative**
- Additional container resource consumption in local Podman environments.

**Risks and mitigation**
- *Risk:* Accidental loss of data during container teardown (`podman-compose down`).
- *Mitigation:* Explicit named volume declaration in `podman-compose.yml` and backup strategy documented in `docs/deployment.md`.

## Verification

Verified by automated tests exercising repository operations, validation of foreign keys/indexes, and successful volume mounting checks in compose configurations.
