# Вебсистема онлайн-замовлень у кав'ярні «Optima Coffee»

[![CI Pipeline](https://github.com/anatolii-dotsenko/optima-practice/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/anatolii-dotsenko/optima-practice/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Google Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-Serverless-4285F4?logo=googlecloud)
![Tests](https://img.shields.io/badge/pytest-50%2F50%20passed-brightgreen)

Програмний комплекс онлайн-замовлень кав'ярні, розроблений у межах виконання індивідуального завдання з навчальної дисципліни **«Технологічна практика. Ч. 1»** (ТОВ «ФК «Оптіма», група КН-44, студент Доценко Анатолій Віталійович).

---

## 🔗 Швидкі посилання

- 📄 **Офіційний звіт з практики (ДСТУ 3008:2015):** [Переглянути в Google Docs](https://docs.google.com/document/d/1Cs6HnUGZj_0T1uJMkrIG5QCZNgycH28b9k-fGj9Tzh8/edit?usp=sharing)
- 🌐 **Робочий вебклієнт (Cloud Run Frontend):** [https://optima-coffee-frontend-ily7vljsqa-lm.a.run.app](https://optima-coffee-frontend-ily7vljsqa-lm.a.run.app)
- 📖 **Інтерактивна специфікація API (Swagger UI):** [https://optima-coffee-backend-ily7vljsqa-lm.a.run.app/api/v1/docs](https://optima-coffee-backend-ily7vljsqa-lm.a.run.app/api/v1/docs)
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

### Варіант 1. Автоматизований хмарний деплой в AWS через CI/CD (Основний / Поточний)

Основний production-ready метод розгортання, керований **GitHub Actions**, **Docker Hub** та **Terraform (IaC)**:

1. **Автоматичний запуск через Git:**
   Будь-який `push` у гілку `rc` або `main` автоматично ініціює повний конвеєр:
   - Проходження 4 рівнів перевірки якості (лінтинг, форматування, 50 тестів Pytest, валідація API).
   - Збірка оптимізованого OCI-образу та його публікація у Docker Hub під тегами `latest` та `${{ github.sha }}`.
   - Створення/синхронізація інфраструктури AWS (`eu-north-1`, `t3.micro`, security group) за допомогою Terraform.
   - Деплой контейнера на EC2 через SSH та фінальна верифікація працездатності (`HTTP 200` на `/health`).

2. **Доступ до розгорнутого сервісу:**
   - **Вебзастосунок:** `http://<EC2_PUBLIC_IP>:8000/`
   - **Інтерактивна документація Swagger:** `http://<EC2_PUBLIC_IP>:8000/api/v1/docs`
   - **Перевірка стану:** `http://<EC2_PUBLIC_IP>:8000/health`
   *(Публічна IP-адреса виводиться на кроці Terraform Apply в GitHub Actions або через `terraform output -raw ec2_public_ip`).*

3. **Локальне керування інфраструктурою Terraform (опціонально):**
   ```bash
   cd infra
   terraform init
   terraform apply
   # Після завершення адреса буде виведена у змінній app_url
   ```

---

### Варіант 2. Автономний локальний запуск у Docker (Офіційний образ)

Застосунок працює повністю автономно без зовнішніх залежностей завдяки вбудованій SQLite БД та автоматичному сідінгу каталогу при старті:

```bash
# 1. Збірка Docker-образу з кореня репозиторію:
docker build -t optima-practice .

# 2. Запуск контейнера:
docker run -d -p 8000:8000 --name optima-practice optima-practice

# 3. Перевірка працездатності сервісу:
curl http://localhost:8000/health
```

- **Вебзастосунок (Frontend UI):** `http://localhost:8000/`
- **Інтерактивна документація API (Swagger):** `http://localhost:8000/api/v1/docs`
- **Healthcheck:** `http://localhost:8000/health`

#### 🔑 Демо-облікові записи (попередньо налаштовані в системі):
- **Кабінет Бариста / Адміністратор:**
  - Email: `barista@optima.coffee`
  - Пароль: `barista123`
  - *Доступні функції:* керування стоп-листом, зміна цін, live-черга замовлень бариста та зміна статусів (`confirmed` $\rightarrow$ `ready` $\rightarrow$ `completed`).
- **Гість (Клієнт):**
  - Email: `customer@optima.coffee`
  - Пароль: `customer123`
  - *Доступні функції:* вибір страв, оформлення замовлення, перегляд історії та статусу в профілі.
*(На сторінці входу `#/login` також доступні кнопки швидкого автозаповнення в 1 клік).*

Зупинка та видалення контейнера:
```bash
docker stop optima-practice && docker rm optima-practice
```

---

### Варіант 3. Локальний запуск для розробки (Development)

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

### Варіант 4. Мультиконтейнерний запуск (Podman / Docker Compose з PostgreSQL)

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

### Варіант 5. Хмарне розгортання в Google Cloud Run

> [!WARNING]
> **DEPRECATED / TODO REFACTORING**: Цей варіант зафіксовано для історії проходження технологічної практики (Sprint 3). Наразі він позначений як застарілий та очікує на плановий рефакторинг під нову уніфіковану схему контейнеризації. Актуальним стандартом хмарного розгортання проєкту є **Варіант 1 (AWS EC2 через Terraform та CI/CD)**.

У [Google Cloud Shell](https://shell.cloud.google.com) достатньо виконати скрипт автоматизації:

```bash
git clone https://github.com/anatolii-dotsenko/optima-practice.git
cd optima-practice/project

export PROJECT_ID="optima-roast"
export REGION="europe-central2"
export DATABASE_URL="postgresql://user:password@host/coffeeshop?sslmode=require"

./deploy/deploy-cloud-run.sh
```

Скрипт налаштовує IAM, збирає OCI-образи через Cloud Build, публікує в Artifact Registry, розгортає бекенд і фронтенд у Cloud Run та налаштовує безпеку CORS.

Детальний архівний гайд: [`project/docs/cloud-run-deployment.md`](project/docs/cloud-run-deployment.md).

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

## ☁️ Інфраструктура AWS (Terraform) та CI/CD Pipeline

У проєкті реалізовано автоматизований DevOps-конвеєр на базі **GitHub Actions**, **Docker Hub**, **Terraform (IaC)** та **AWS EC2**.

### 1. Архітектура та параметри хмарної інфраструктури (AWS)
- **Модель розгортання:** єдиний легковагий уніфікований OCI/Docker контейнер (FastAPI бекенд + роздача SPA-клієнта на порті 8000).
- **База даних:** дуальна стратегія збереження даних ([ADR-0010](project/docs/adr/0010-dual-database-strategy-and-zero-config-sqlite-runtime.md)):
  - *Autonomous Zero-Config Mode (SQLite):* використовується за замовчуванням у Docker-образі для EC2 (`sqlite:////home/appuser/coffeeshop.db`). Споживає лише ~70–90 МБ RAM, що ідеально підходить для `t3.micro` (1 ГБ RAM) та унеможливлює OOM-збої. На старті контейнера автоматично накладається схема та сідяться демо-акаунти.
  - *Enterprise Mode (PostgreSQL 16):* активується під час передачі рядка `DATABASE_URL=postgresql://...` для багатоконтейнерних та серверлес-середовищ (Podman Compose, Cloud Run + Cloud SQL, [ADR-0004](project/docs/adr/0004-postgresql-and-persistence-strategy.md)).
- **Регіон AWS:** `eu-north-1` (Стокгольм)
- **AMI ID:** `ami-0705384c0b33c194c` (Ubuntu Server 24.04/22.04 LTS)
- **Тип інстансу:** `t3.micro` (1 vCPU, 1 GB RAM, Burstable)
- **SSH Key Pair:** `devops-key`
- **Security Group:** порти `22` (SSH), `8000` (Application Web + REST API), `80` (HTTP), вихідний трафік відкритий.
- **Ініціалізація (User Data):** автоматичне встановлення та запуск Docker Engine на віртуальній машині.

Конфігураційні файли розташовані у теці [`infra/`](infra/):
- `providers.tf` — налаштування AWS провайдера.
- `variables.tf` — змінні інфраструктури.
- `main.tf` — Security Group та EC2 інстанс з `user_data`.
- `outputs.tf` — експорт публічної IP-адреси та URL додатку.
- `terraform.tfvars.example` — приклад значень змінних.

Локальна перевірка та ініціалізація Terraform:
```bash
cd infra
terraform init
terraform fmt -check
terraform plan
```

### 2. Необхідні GitHub Secrets

Для роботи автоматичного CI/CD пайплайну у налаштуваннях репозиторію (**Settings → Secrets and variables → Actions**) мають бути задані наступні секрети:

| Назва секрету | Призначення | Приклад / Формат |
|---|---|---|
| `DOCKER_USERNAME` | Ім'я користувача на Docker Hub | `your_dockerhub_user` |
| `DOCKER_TOKEN` | Персональний Access Token Docker Hub (з правами Read/Write) | `dckr_pat_...` |
| `AWS_ACCESS_KEY_ID` | Ключ доступу AWS IAM (з правами керування EC2/VPC) | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Секретний ключ AWS IAM | `wJalrXUtnFEMI/K7MDENG/...` |
| `EC2_SSH_KEY_B64` | Приватний ключ `devops-key.pem` у форматі Base64 | `cat devops-key.pem \| base64` |

> [!NOTE]
> Щоб закодувати приватний ключ у Base64:
> - На macOS: `base64 -i devops-key.pem | pbcopy`
> - На Linux: `base64 -w0 devops-key.pem | xclip -sel clip`

### 3. Етапи конвеєра GitHub Actions (`.github/workflows/ci.yml`)

```text
┌───────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ 1. backend-checks │ ──> │  2. build-and-push   │ ──> │ 3. terraform-apply  │ ──> │      4. deploy      │
│  - Ruff lint/fmt  │     │  - Multi-stage OCI   │     │  - AWS eu-north-1   │     │  - SSH over Base64  │
│  - Pytest (50/50) │     │  - Push Docker Hub   │     │  - Auto-sync state  │     │  - Docker run/pull  │
│  - OpenAPI check  │     │  - tags: latest, sha │     │  - Export EC2 IP    │     │  - Healthcheck 200  │
└───────────────────┘     └──────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

1. **`backend-checks` (Quality Gates):** лінтинг (Ruff), перевірка форматування, виконання 50 тестів Pytest, валідація наявності OpenAPI документації.
2. **`build-and-push`:** збірка оптимізованого multi-stage Docker образу та публікація у Docker Hub з тегами `latest` та `${{ github.sha }}`.
3. **`terraform-apply`:** автоматичне ідемпотентне розгортання інфраструктури в AWS (`eu-north-1`) із механізмом синхронізації/імпорту стану (`terraform import`) та експортом публічної IP-адреси.
4. **`deploy`:** безпечне підключення по SSH за допомогою `EC2_SSH_KEY_B64`, очікування готовності Docker-демона, завантаження свіжого образу з Docker Hub, запуск контейнера (`--restart unless-stopped`) та верифікація працездатності через `http://<EC2_IP>:8000/health`.

Детальний опис архітектурного рішення зафіксовано в **[ADR-0009](project/docs/adr/0009-automated-ci-cd-pipeline-with-github-actions-docker-hub-and-terraform.md)**.

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
  - [ADR-0009: Автоматизований CI/CD конвеєр (GitHub Actions, Docker Hub, Terraform, AWS EC2)](project/docs/adr/0009-automated-ci-cd-pipeline-with-github-actions-docker-hub-and-terraform.md)
  - [ADR-0010: Дуальна стратегія баз даних та автономний SQLite runtime](project/docs/adr/0010-dual-database-strategy-and-zero-config-sqlite-runtime.md)
- **Документація REST API:** [`project/docs/api/README.md`](project/docs/api/README.md) ([OpenAPI 3.1 openapi.yaml](project/docs/api/openapi.yaml))