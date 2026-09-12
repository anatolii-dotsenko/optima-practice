# ІНСТРУКЦІЯ З РОЗГОРТАННЯ В GOOGLE CLOUD RUN
## Вебсистема онлайн-замовлень у кав’ярні «Optima Coffee»

У цій інструкції описано повний покроковий процес розгортання вебсистеми «Optima Coffee» на платформі **Google Cloud Run** — сучасному безсерверному (serverless) середовищі виконання контейнерів OCI.

---

## 1 Загальна архітектура в Google Cloud

Система розгортається у вигляді взаємопов'язаних сервісів:
1. **База даних (Database Tier):** Реляційна СУБД PostgreSQL 16:
   - *Варіант А (Рекомендований у GCP):* **Google Cloud SQL for PostgreSQL** (повністю керований екземпляр у GCP).
   - *Варіант Б (Швидкий / Безкоштовний для практики):* Керована хмарна СУБД (наприклад, [Neon.tech](https://neon.tech), [Supabase](https://supabase.com) або [Aiven](https://aiven.io)), яка надає прямий connection string `DATABASE_URL`.
2. **Бекенд (Backend API Tier):** Сервіс Cloud Run `optima-coffee-backend` на базі Python 3.12 + FastAPI (порт 8000). Автоматично маштабується від 0 до $N$ екземплярів.
3. **Фронтенд (Frontend Client Tier):** Сервіс Cloud Run `optima-coffee-frontend` на базі Nginx unprivileged (порт 8080), що роздає статичні файли Single Page Application (SPA).

---

## 2 Передумови (Prerequisites)

1. **Акаунт Google Cloud:** активний обліковий запис у [Google Cloud Console](https://console.cloud.google.com/) із прив'язаним платіжним профілем (Cloud Run має щедрий безкоштовний ліміт **Free Tier**: 2 млн запитів/місяць, 360,000 ГБ-с RAM, 180,000 vCPU-с щомісяця безкоштовно).
2. **Інструмент керування (на вибір):**
   - **Google Cloud Shell (Рекомендовано):** вбудований термінал безпосередньо у браузері на [shell.cloud.google.com](https://shell.cloud.google.com). *Не потребує встановлення жодного ПЗ на ваш комп'ютер*, утиліта `gcloud`, `docker` та `git` уже встановлені та авторизовані.
   - **Локальний `gcloud CLI`:** встановлений Google Cloud SDK на вашому ПК ([інструкція з встановлення](https://cloud.google.com/sdk/docs/install)).

---

## 3 Покрокове розгортання

### Крок 1. Авторизація та налаштування проєкту GCP

Відкрийте Cloud Shell або термінал та виконайте:

```bash
# 1. Авторизуватися в Google Cloud (якщо запускаєте локально)
gcloud auth login

# 2. Створити новий проєкт (або використати існуючий)
# Замініть YOUR_PROJECT_ID на унікальний ідентифікатор, наприклад: optima-coffee-12345
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="europe-west1"   # Доступні регіони: europe-west1 (Бельгія), europe-central2 (Варшава), etc.

gcloud projects create $PROJECT_ID --name="Optima Coffee" 2>/dev/null || true
gcloud config set project $PROJECT_ID

# 3. Увімкнути необхідні Cloud API сервіси
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    sqladmin.googleapis.com
```

---

### Крок 2. Налаштування бази даних PostgreSQL

Оскільки Cloud Run є stateless-середовищем, база даних має працювати персистентно.

#### Варіант А: Швидкий старт через безкоштовний Neon / Supabase (Найпростіший)
1. Зареєструйте безкоштовний екземпляр PostgreSQL на [neon.tech](https://neon.tech) або [supabase.com](https://supabase.com).
2. Створіть нову базу даних `coffeeshop`.
3. Скопіюйте Connection String:
   ```bash
   export DATABASE_URL="postgresql://username:password@ep-sample-pooler.eu-central-1.aws.neon.tech/coffeeshop?sslmode=require"
   ```

#### Варіант Б: Google Cloud SQL (Повністю в екосистемі Google Cloud)
```bash
# 1. Створити екземпляр Cloud SQL PostgreSQL 16
gcloud sql instances create optima-postgres \
    --database-version=POSTGRES_16 \
    --tier=db-f1-micro \
    --region=$REGION \
    --root-password="SuperSecurePassword123!"

# 2. Створити базу даних coffeeshop
gcloud sql databases create coffeeshop --instance=optima-postgres

# 3. Отримати connection name екземпляра
export INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe optima-postgres --format='value(connectionName)')

# 4. Рядок підключення для Cloud Run через Unix Domain Socket:
export DATABASE_URL="postgresql://postgres:SuperSecurePassword123!@/coffeeshop?host=/cloudsql/${INSTANCE_CONNECTION_NAME}"
```

---

### Крок 3. Створення реєстру контейнерів Artifact Registry

```bash
# Створення репозиторію образів у вашому регіоні
gcloud artifacts repositories create optima-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Optima Coffee services" 2>/dev/null || true
```

---

### Крок 4. Збірка та розгортання Бекенду (FastAPI)

1. Перейдіть до кореневої директорії проєкту `project/`:
   ```bash
   cd project
   ```

2. Зберіть та надішліть образ бекенду в Google Artifact Registry за допомогою **Google Cloud Build** (збірка відбувається на серверах Google, не навантажуючи ваш комп'ютер):
   ```bash
   export BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/optima-repo/coffee-backend:latest"

   gcloud builds submit . \
       --config=deploy/cloudbuild-backend.yaml \
       --substitutions=_IMAGE="${BACKEND_IMAGE}"
   ```

3. Розгорніть бекенд у Cloud Run:
   ```bash
   gcloud run deploy optima-coffee-backend \
       --image=$BACKEND_IMAGE \
       --region=$REGION \
       --platform=managed \
       --allow-unauthenticated \
       --port=8000 \
       --memory=512Mi \
       --cpu=1 \
       --min-instances=0 \
       --max-instances=3 \
       --set-env-vars="DATABASE_URL=${DATABASE_URL},SECRET_KEY=production-secure-key-32chars-min-jwt-secret,ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=60,ENVIRONMENT=production,BACKEND_CORS_ORIGINS=*"
   ```
   *(Примітка: якщо ви використовуєте Cloud SQL, додайте прапорець `--add-cloudsql-instances=$INSTANCE_CONNECTION_NAME`).*

4. Збережіть отриману публічну HTTPS-адресу бекенду:
   ```bash
   export BACKEND_URL=$(gcloud run services describe optima-coffee-backend --region=$REGION --format='value(status.url)')
   echo "Бекенд успішно розгорнуто: ${BACKEND_URL}"
   echo "Документація Swagger UI: ${BACKEND_URL}/api/v1/docs"
   ```

*Примітка щодо наповнення бази даних:* Під час першого запуску бекенду механізм `lifespan` автоматично створить усі таблиці та заповнить базу початковими стравами меню й категоріями (`app/seed.py`).

---

### Крок 5. Збірка та розгортання Фронтенду (Vanilla JS SPA)

1. Оновіть конфігурацію клієнта `project/frontend/config.js`, вказавши URL розгорнутого бекенду:
   ```bash
   cat <<EOF > frontend/config.js
   // Runtime environment configuration for Optima Coffee Web Client
   window.__APP_CONFIG__ = window.__APP_CONFIG__ || {
     API_BASE_URL: "${BACKEND_URL}/api/v1",
   };
   EOF
   ```

2. Зберіть образ фронтенду в Google Cloud Build:
   ```bash
   export FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/optima-repo/coffee-frontend:latest"

    gcloud builds submit . \
        --config=deploy/cloudbuild-frontend.yaml \
        --substitutions=_IMAGE="${FRONTEND_IMAGE}"
    ```

3. Розгорніть фронтенд у Cloud Run:
    ```bash
    gcloud run deploy optima-coffee-frontend \
        --image=$FRONTEND_IMAGE \
        --region=$REGION \
        --allow-unauthenticated \
       --port=8080 \
       --memory=256Mi \
       --cpu=1 \
       --min-instances=0 \
       --max-instances=3
   ```

4. Отримайте публічну адресу сайту:
   ```bash
   export FRONTEND_URL=$(gcloud run services describe optima-coffee-frontend --region=$REGION --format='value(status.url)')
   echo "=========================================================="
   echo "Сайт кав'ярні Optima Coffee успішно працює в Google Cloud!"
   echo "Вебклієнт (Frontend): ${FRONTEND_URL}"
   echo "REST API (Backend):   ${BACKEND_URL}/api/v1/docs"
   echo "=========================================================="
   ```

---

### Крок 6. Фінальне налаштування безпеки CORS

Для дотримання безпеки оновіть дозволені джерела запитів на бекенді, замінивши `*` на точну адресу фронтенду:
```bash
gcloud run services update optima-coffee-backend \
    --region=$REGION \
    --update-env-vars="BACKEND_CORS_ORIGINS=${FRONTEND_URL},http://localhost:3000"
```

---

## 4 Автоматизований скрипт розгортання

У директорії `deploy/` підготовлено скрипт автоматизації [`deploy/deploy-cloud-run.sh`](../deploy/deploy-cloud-run.sh).

Для повного розгортання достатньо виконати:
```bash
chmod +x deploy/deploy-cloud-run.sh
./deploy/deploy-cloud-run.sh
```

---

## 5 Керування, діагностика та перегляд логів

1. **Перегляд логів бекенду в реальному часі:**
   ```bash
   gcloud run services logs tail optima-coffee-backend --region=$REGION
   ```
2. **Перегляд логів фронтенду:**
   ```bash
   gcloud run services logs tail optima-coffee-frontend --region=$REGION
   ```
3. **Моніторинг через вебінтерфейс Console:**
   Відкрийте [Google Cloud Run Console](https://console.cloud.google.com/run), де доступні графіки завантаження CPU, кількості запитів, затримок відгуку та лічильника активних екземплярів.
