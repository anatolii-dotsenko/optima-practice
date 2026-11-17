# ==============================================================================
# Multi-stage Dockerfile for Optima Coffee Web Application & API
# ==============================================================================

# Stage 1: Build dependencies
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY project/backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production runtime image
FROM python:3.12-slim-bookworm AS runner

# Create non-root system user and group
RUN groupadd -r -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -d /home/appuser -m -s /sbin/nologin appuser

WORKDIR /app

# Install runtime dependencies (libpq for postgres, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    DATABASE_URL="sqlite:////home/appuser/coffeeshop.db" \
    PORT=8000

# Copy backend application and frontend assets
COPY --chown=appuser:appgroup project/backend/app /app/app
COPY --chown=appuser:appgroup project/backend/pyproject.toml /app/pyproject.toml
COPY --chown=appuser:appgroup project/frontend /app/frontend

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
