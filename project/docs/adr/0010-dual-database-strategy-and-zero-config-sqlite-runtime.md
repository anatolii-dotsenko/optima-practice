# ADR-0010: Dual Database Strategy and Zero-Config SQLite Runtime

- **Status:** accepted
- **Date:** 2026-11-17
- **Deciders:** Engineering & Architecture Team
- **Related requirements:** NFR-01 (Modularity), NFR-02 (Maintainability), NFR-05 (Resource Efficiency & Low Footprint)

## Context

The Optima Coffee platform was originally architected with PostgreSQL 16 as its primary database tier (ADR-0004), suitable for multi-container deployments (Podman Compose) and managed enterprise clouds (Google Cloud SQL).

However, introducing automated CI/CD deployments to AWS EC2 `t3.micro` instances introduces critical resource constraints:
1. An AWS `t3.micro` instance has only **1 GB of total RAM**. Running an operating system (Ubuntu 24.04), Docker daemon, PostgreSQL container, FastAPI application, and reverse proxy simultaneously can exhaust available memory and trigger Linux Out-Of-Memory (OOM) killer terminations.
2. Academic and CI/CD demonstration environments do not require permanent data retention across restarts. Reverting to a pristine baseline state with pre-populated demo data on each restart is desirable for repeatable grading and evaluations.
3. Local developers and evaluators require a zero-configuration option (`docker run -p 8000:8000 ...`) that starts instantaneously without requiring a separate PostgreSQL instance or complex connection strings.

## Decision

We adopt a **Dual Database Strategy** with SQLAlchemy 2.0 ORM:

1. **Production Enterprise Mode (PostgreSQL 16):**
   - Activated whenever `DATABASE_URL` is set to a `postgresql://` connection string.
   - Used for Google Cloud Run (with Google Cloud SQL) and local Podman Compose (with persistent `pgdata` volume).
   - Enforces ACID transactions, strict relational constraints, and connection pooling.

2. **Autonomous Zero-Config Mode (SQLite):**
   - Configured as the default runtime (`sqlite:///./coffeeshop.db` locally, `sqlite:////home/appuser/coffeeshop.db` in the official Docker image).
   - Utilizes `connect_args={"check_same_thread": False}` for multi-threaded FastAPI execution.
   - On application startup (`lifespan`), the system automatically provisions all tables (`Base.metadata.create_all`) and executes the initial catalog and user seed (`app.seed.seed_initial_data`).
   - Automatically seeds:
     - Full coffee shop menu (Coffee, Tea, Bakery, Desserts).
     - Demo Barista / Admin account (`barista@optima.coffee` / `barista123`).
     - Demo Customer account (`customer@optima.coffee` / `customer123`) with a live pre-populated order in the queue.

## Considered alternatives

| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| **Dual Strategy (PostgreSQL for enterprise, SQLite for zero-config/EC2)** | Extreme flexibility, zero-overhead startup, ~70 MB RAM footprint, full compatibility across environments | Requires testing ORM compatibility across SQLite and PostgreSQL | **Chosen.** Solves memory constraints on `t3.micro` while maintaining enterprise PostgreSQL capability. |
| Mandatory PostgreSQL Container Everywhere | 100% dialect parity between dev, test, and cloud | Consumes 200–300 MB extra RAM, high risk of OOM on `t3.micro`, requires volume management | Rejected due to memory overhead and unnecessary complexity for standalone demo runs. |
| SQLite Only (Drop PostgreSQL) | Simplest architecture, lowest complexity | Lacks enterprise concurrency, cannot support horizontal scaling across multiple container instances | Rejected because enterprise scalability and Cloud SQL integration remain strategic project goals. |

## Consequences

**Positive**
- Single-container Docker deployment runs in ~70–90 MB RAM, leaving >800 MB free on AWS `t3.micro`.
- Zero-config local execution: `docker run -p 8000:8000 <image>` works out of the box with zero external dependencies.
- Demo access to the Barista dashboard is ready immediately upon container boot.

**Negative**
- SQLite does not support high-concurrency writes and does not provide native network socket clustering.
- Without a mounted volume, SQLite data resets to the initial seed state upon container restart (accepted per requirement).

## Verification

Verified via:
1. Unit and integration tests (50/50 passing against in-memory SQLite).
2. Local and containerized startup tests validating automatic schema creation and catalog/user seeding.
3. Successful live deployment on AWS EC2 `t3.micro` under memory pressure.
