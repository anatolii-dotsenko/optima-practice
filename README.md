# Optima Practice AI Agent — Coffee Shop Online Ordering System

Repository for the software engineering practice project ("Технологічна практика. Ч. 1") conforming to ДСТУ 3008:2015.

The complete software project, specifications, architecture documentation, and deployment files are located in the [`project/`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/) directory:

- **Project Entry & Quick Start:** [`project/README.md`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/README.md)
- **Backend Service:** [`project/backend/`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/backend/)
- **Frontend Client:** [`project/frontend/`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/frontend/)
- **Containerization (Podman):** [`project/deploy/`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/deploy/)
- **Practice Report (Markdown):** [`project/report.md`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/report.md)
- **Practice Report (Google Docs, ДСТУ 3008:2015):** [Google Docs Document](https://docs.google.com/document/d/1Cs6HnUGZj_0T1uJMkrIG5QCZNgycH28b9k-fGj9Tzh8/edit?usp=sharing)
- **Technical Specification:** [`project/docs/technical-specification.md`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/technical-specification.md)
- **User Manual:** [`project/docs/user-manual.md`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/user-manual.md)
- **Architecture Decision Records:** [`project/docs/adr/`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/adr/)
- **API Reference (OpenAPI 3.1):** [`project/docs/api/`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/api/)
- **Google Cloud Run Deployment Guide:** [`project/docs/cloud-run-deployment.md`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/cloud-run-deployment.md)
- **Practice Specification Set:** [`project/report-spec/`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/report-spec/)

---

## Хмарне розгортання в Google Cloud Platform (GCP)

Проєкт повністю адаптовано для безсерверного (serverless) функціонування в **Google Cloud Run** з базою даних **PostgreSQL 16** (Google Cloud SQL або serverless Neon/Supabase):

```text
[Користувач / Браузер]
         │
         ├──► Cloud Run (Frontend SPA: Nginx, порт 8080, HTTPS)
         │            │
         │            ▼ REST API запити
         └──► Cloud Run (Backend API: FastAPI / Uvicorn, порт 8000/8080, HTTPS)
                      │
                      ▼ SQLAlchemy 2.0 (SSL / Unix Domain Socket)
         PostgreSQL 16 (Google Cloud SQL або Serverless Neon / Supabase)
```

### Автоматичний запуск у Google Cloud Shell:
```bash
cd project
export PROJECT_ID="optima-roast"
export REGION="europe-central2"
export DATABASE_URL="postgresql://user:password@host/coffeeshop?sslmode=require"

./deploy/deploy-cloud-run.sh
```

Детальна інструкція: [`project/docs/cloud-run-deployment.md`](file:///Users/liu/Developer/Agents_workspace/Optima/optima-practice-ai-agent/project/docs/cloud-run-deployment.md).