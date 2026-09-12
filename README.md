# Вебсистема онлайн-замовлень у кав'ярні «Optima Coffee»

[![CI Pipeline](https://github.com/anatolii-dotsenko/optima-practice/actions/workflows/ci.yml/badge.svg)](https://github.com/anatolii-dotsenko/optima-practice/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Google Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-Serverless-4285F4?logo=googlecloud)
![Tests](https://img.shields.io/badge/pytest-50%2F50%20passed-brightgreen)

Програмний комплекс онлайн-замовлень кав'ярні, розроблений у межах виконання індивідуального завдання з навчальної дисципліни **«Технологічна практика. Ч. 1»** (ТОВ «ФК «Оптіма», група КН-44, студент Доценко Анатолій Віталійович).

---

## 🔗 Швидкі посилання

- 📄 **Офіційний звіт з практики (ДСТУ 3008:2015):** [Переглянути в Google Docs](https://docs.google.com/document/d/1Cs6HnUGZj_0T1uJMkrIG5QCZNgycH28b9k-fGj9Tzh8/edit?usp=sharing)
- 🌐 **Робочий вебклієнт (Cloud Run Frontend):** [https://optima-coffee-frontend-139026558151.europe-central2.run.app](https://optima-coffee-frontend-139026558151.europe-central2.run.app)
- 📖 **Інтерактивна специфікація API (Swagger UI):** [https://optima-coffee-backend-139026558151.europe-central2.run.app/api/v1/docs](https://optima-coffee-backend-139026558151.europe-central2.run.app/api/v1/docs)
- 🚀 **Інструкція з хмарного розгортання:** [`project/docs/cloud-run-deployment.md`](project/docs/cloud-run-deployment.md)

---

## ☕ Можливості системи

1. **Каталог страв та напоїв:** динамічне меню за категоріями (кава, чаї, десерти, авторські напої), склад, фотографії та актуальні ціни.
2. **Стоп-лист та доступність:** керування наявністю позицій у реальному часі.
3. **Безпечна авторизація клієнтів:** реєстрація, вхід за стандартом RFC 7519 (JWT Bearer Token), хешування паролів (bcrypt, 12 раундів).
4. **Кошик та серверний розрахунок цін:** захист від маніпуляцій на стороні клієнта, валідація суми замовлення виключно на бекенді.
5. **Життєвий цикл замовлення:** скінченний автомат переходів статусів (`created` → `pending_payment` → `paid` → `preparing` → `ready` → `completed` / `cancelled`).
6. **Панель персоналу / бариста:** розмежування доступу на основі ролей (RBAC), перегляд черги замовлень та зміна статусів видачі.

---

## 🛠 Технологічний стек

- **Бекенд (REST API):** Python 3.12+, FastAPI, SQLAlchemy 2.0 (Core & ORM), Pydantic v2 (DTO валідація), Alembic, PyJWT, Passlib/Bcrypt.
- **Фронтенд (Web Client SPA):** HTML5, Vanilla JavaScript (ES Modules, нативний Fetch API, без сторонніх важких фреймворків), Vanilla CSS з власною системою дизайн-токенів (`tokens.css`, адаптивна верстка).
- **База даних:** PostgreSQL 16 (Google Cloud SQL у хмарі / OCI-контейнер локально) + SQLite (в пам'яті для ізольованого модульного тестування).
- **Контейнеризація:** Podman / Podman Compose (rootless, non-root користувач `appuser`, багатоетапні збірки Multi-stage).
- **Хмарна інфраструктура:** Google Cloud Run (Serverless OCI контейнери), Google Artifact Registry, Google Cloud Build, Google Cloud SQL for PostgreSQL 16.
- **DevOps & Якість:** GitHub Actions CI (4 Quality Gates), Pytest (50 тестів), Ruff (лінтинг і форматування коду).

---

## 🏛 Архітектура системи

Система побудована за суворою **трирівневою компонентною архітектурою (Three-Tier Architecture)**:

```text
[ Користувач / Браузер ]
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Рівень представлення (Presentation / Frontend Tier)        │
│  - SPA Web Client (Vanilla JS, CSS Tokens, Responsive UI)   │
│  - Nginx unprivileged (HTTP static runtime, порт 8080)      │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTPS / REST API JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Рівень бізнес-логіки (Application / Backend API Tier)       │
│  - HTTP Handlers / Routers (FastAPI, Pydantic DTOs)         │
│  - Service Layer (Domain logic, State Machine, Security)    │
│  - Repository Layer (SQLAlchemy 2.0, чисті SQL-запити)      │
└─────────────────────────────┬───────────────────────────────┘
                              │ TCP / Unix Domain Socket (SSL)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Рівень даних (Data / Persistence Tier)                     │
│  - PostgreSQL 16 (Таблиці: users, categories, items, orders)│
└─────────────────────────────────────────────────────────────┘
```

### Затверджені архітектурні обмеження:
1. `api -> services -> repositories -> database` — прямий зв'язок без перескакування шарів.
2. Сервісний шар (`services/`) не імпортує вебфреймворк FastAPI/Starlette і містить чисту бізнес-логіку.
3. Шар репозиторіїв (`repositories/`) — єдине місце побудови SQL-запитів.
4. Моделі ORM ніколи не повертаються на фронтенд безпосередньо, а трансформуються в типізовані схеми Pydantic DTO.

---

## 📁 Структура проєкту

```text
optima-practice/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI (Quality Gates, 50 тестів)
├── project/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/             # HTTP роутинг, статус-коди, DTO (v1)
│   │   │   ├── core/            # Конфігурація (BaseSettings), безпека (JWT), логування, БД
│   │   │   ├── models/          # ORM моделі SQLAlchemy (User, Category, MenuItem, Order)
│   │   │   ├── repositories/    # Шар абстракції доступу до даних (SQL-запити)
│   │   │   ├── schemas/         # Валідаційні Pydantic DTO (In/Out)
│   │   │   ├── services/        # Чиста предметна бізнес-логіка
│   │   │   ├── seed.py          # Автоматичне первинне наповнення каталогу
│   │   │   └── main.py          # Точка входу FastAPI (lifespan, CORS, exceptions)
│   │   ├── tests/               # Набір із 50 модульних та інтеграційних тестів
│   │   ├── requirements.txt     # Фіксовані залежності Python
│   │   └── pyproject.toml       # Конфігурація pytest, ruff та coverage
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── api/             # Ізольований клієнт REST API (без захардкодних URL)
│   │   │   ├── components/      # UI компоненти (Navbar, CartModal, Alert тощо)
│   │   │   ├── pages/           # Екрани (меню, замовлення, вхід, реєстрація)
│   │   │   ├── styles/          # Дизайн-токени (tokens.css, main.css)
│   │   │   └── main.js          # SPA-маршрутизатор та обробка стану
│   │   ├── config.js            # Динамічна конфігурація оточення (API Base URL)
│   │   └── index.html           # Головна точка входу SPA
│   ├── deploy/
│   │   ├── Containerfile.backend    # Multi-stage Dockerfile для FastAPI (non-root)
│   │   ├── Containerfile.frontend   # Unprivileged Nginx runtime (порт 8080)
│   │   ├── cloudbuild-backend.yaml  # Конфігурація Google Cloud Build для бекенду
│   │   ├── cloudbuild-frontend.yaml # Конфігурація Google Cloud Build для фронтенду
│   │   ├── deploy-cloud-run.sh      # Автоматизований bash-скрипт деплою в Cloud Run
│   │   └── podman-compose.yml       # Локальна оркестрація з томом для PostgreSQL
│   ├── docs/
│   │   ├── adr/                 # Архітектурні рішення (ADR-0001 — ADR-0008)
│   │   ├── api/                 # Специфікація OpenAPI 3.1 та документація ендпоінтів
│   │   ├── architecture.puml    # PlantUML діаграма компонентної архітектури
│   │   ├── database-schema.puml # PlantUML ER-діаграма структури реляційної БД
│   │   ├── diagrams.md          # Опис діаграм відповідно до ДСТУ
│   │   ├── cloud-run-deployment.md # Повний гайд з розгортання в Google Cloud
│   │   ├── technical-specification.md # Технічне завдання (ТЗ)
│   │   ├── user-manual.md       # Посібник користувача та бариста
│   │   ├── test-report.md       # Протокол тестування (50/50 тестів)
│   │   └── defect-log.md        # Журнал виявлених та усунених дефектів
│   └── report-spec/             # Специфікації та нормативні вимоги практики
└── README.md                    # Єдина документація репозиторію
```

---

## 🚀 Інструкція з запуску

### Варіант А. Локальний запуск для розробки

#### 1. Бекенд:
```bash
cd project/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest ruff

# Запуск тестів (50 тестів):
PYTHONPATH=. pytest tests -v

# Запуск локального сервера:
uvicorn app.main:app --reload --port 8000
```
- Swagger UI доступний за адресою: `http://localhost:8000/api/v1/docs`
- Healthcheck: `http://localhost:8000/health`

#### 2. Фронтенд:
```bash
cd project/frontend
python3 -m http.server 3000
# Відкрийте у браузері http://localhost:3000
```

---

### Варіант Б. Локальний запуск у контейнерах (Podman / Docker)

```bash
cd project
cp .env.example .env

# Підняти СУБД PostgreSQL, бекенд і фронтенд:
podman-compose -f deploy/podman-compose.yml up -d

# Перевірити статус контейнерів:
podman ps
```
- Вебклієнт: `http://localhost:3000`
- REST API: `http://localhost:8000/api/v1/docs`

---

### Варіант В. Хмарне розгортання в Google Cloud Run

У [Google Cloud Shell](https://shell.cloud.google.com) достатньо виконати скрипт автоматизації:

```bash
git clone https://github.com/anatolii-dotsenko/optima-practice.git
cd optima-practice/project

export PROJECT_ID="optima-roast"
export REGION="europe-central2"
export DATABASE_URL="postgresql://user:password@host/coffeeshop?sslmode=require"

./deploy/deploy-cloud-run.sh
```

Скрипт самостійно налаштовує IAM, збирає OCI-образи через Cloud Build, публікує в Artifact Registry, розгортає бекенд і фронтенд у Cloud Run та налаштовує безпеку CORS.

Детальний покроковий гайд: [`project/docs/cloud-run-deployment.md`](project/docs/cloud-run-deployment.md).

---

## 🧪 Забезпечення якості та тестування

Репозиторій захищено безперервною інтеграцією (CI Pipeline):

- **50 автоматизованих тестів:**
  - `tests/unit/test_security.py` — криптографічне хешування та генерація JWT.
  - `tests/unit/test_auth_service.py` — автентифікація, дублікати email, валідація.
  - `tests/unit/test_menu_service.py` — каталогізація страв, управління стоп-листом.
  - `tests/unit/test_order_service.py` — скінченний автомат статусів замовлень, серверний перерахунок цін.
  - `tests/integration/test_auth_api.py` — HTTP-запити реєстрації, входу, читання профілю.
  - `tests/integration/test_menu_api.py` — перевірка публічних маршрутів та блокування доступу без прав адміна (403 Forbidden).
  - `tests/integration/test_orders_api.py` — повний наскрізний цикл створення та оновлення замовлень.
- **Статичний аналіз коду:** Ruff (PEP 8, безпека, виявлення невикористаного коду).

---

## 📚 Повний перелік документації

- **Звіт з практики (ДСТУ 3008:2015):** [Документ Google Docs](https://docs.google.com/document/d/1Cs6HnUGZj_0T1uJMkrIG5QCZNgycH28b9k-fGj9Tzh8/edit?usp=sharing)
- **Технічне завдання (ТЗ):** [`project/docs/technical-specification.md`](project/docs/technical-specification.md)
- **Архітектурні діаграми:** [`project/docs/diagrams.md`](project/docs/diagrams.md) ([Компонентна архітектура](project/docs/architecture.puml) | [Схема БД](project/docs/database-schema.puml))
- **Посібник користувача та бариста:** [`project/docs/user-manual.md`](project/docs/user-manual.md)
- **Протокол тестування:** [`project/docs/test-report.md`](project/docs/test-report.md)
- **Журнал дефектів:** [`project/docs/defect-log.md`](project/docs/defect-log.md)
- **Інструкція з Google Cloud Run:** [`project/docs/cloud-run-deployment.md`](project/docs/cloud-run-deployment.md)
- **Архітектурні рішення (ADR):**
  - [ADR-0001: Трирівнева архітектура](project/docs/adr/0001-three-tier-architecture.md)
  - [ADR-0002: Вибір FastAPI](project/docs/adr/0002-fastapi-backend-framework.md)
  - [ADR-0003: Відтермінування Go Edge Service](project/docs/adr/0003-deferring-secondary-go-edge-service.md)
  - [ADR-0004: Стратегія персистентності PostgreSQL](project/docs/adr/0004-postgresql-and-persistence-strategy.md)
  - [ADR-0005: Автентифікація JWT та хешування паролів](project/docs/adr/0005-jwt-auth-and-password-hashing.md)
  - [ADR-0006: Скінченний автомат життєвого циклу замовлень](project/docs/adr/0006-order-state-machine-and-lifecycle.md)
  - [ADR-0007: Серверний розрахунок цін та валідація кошика](project/docs/adr/0007-server-side-price-calculation-and-cart-validation.md)
  - [ADR-0008: Розмежування ролей та адміністративні межі (RBAC)](project/docs/adr/0008-role-based-access-control-and-administrative-boundaries.md)
- **Документація REST API:** [`project/docs/api/README.md`](project/docs/api/README.md) ([OpenAPI 3.1 openapi.yaml](project/docs/api/openapi.yaml))