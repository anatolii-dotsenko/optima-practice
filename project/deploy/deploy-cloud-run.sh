#!/usr/bin/env bash
# ==============================================================================
# Deployment Script for Optima Coffee Web System to Google Cloud Run
# ==============================================================================
set -euo pipefail

# Text colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================================${NC}"
echo -e "${BLUE}  Optima Coffee — Google Cloud Run Automated Deployment Script   ${NC}"
echo -e "${BLUE}=================================================================${NC}"

# Check prerequisites
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: 'gcloud' CLI is not installed or not in PATH.${NC}"
    echo "Please install Google Cloud SDK or run this script in Google Cloud Shell:"
    echo "https://shell.cloud.google.com"
    exit 1
fi

# Ensure we are inside project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# GCP Project ID
GCP_PROJECT="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
if [ -z "${GCP_PROJECT}" ] || [ "${GCP_PROJECT}" = "(unset)" ]; then
    echo -e "${YELLOW}GCP Project is not configured.${NC}"
    read -rp "Enter your Google Cloud Project ID: " GCP_PROJECT
    gcloud config set project "${GCP_PROJECT}"
fi
echo -e "${GREEN}✓ Using GCP Project:${NC} ${GCP_PROJECT}"

# Region (default: europe-west1)
GCP_REGION="${REGION:-europe-west1}"
echo -e "${GREEN}✓ Using GCP Region:${NC} ${GCP_REGION}"

# Database URL check
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "\n${YELLOW}Database connection string (DATABASE_URL) is required.${NC}"
    echo "Example (Neon / Supabase): postgresql://user:password@host.neon.tech/coffeeshop?sslmode=require"
    echo "Example (Cloud SQL): postgresql://postgres:password@/coffeeshop?host=/cloudsql/PROJECT:REGION:INSTANCE"
    read -rp "Enter DATABASE_URL: " DATABASE_URL
    if [ -z "${DATABASE_URL}" ]; then
        echo -e "${RED}Error: DATABASE_URL cannot be empty.${NC}"
        exit 1
    fi
fi

# Artifact Registry Repo
REPO_NAME="optima-repo"
BACKEND_IMG="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/coffee-backend:latest"
FRONTEND_IMG="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/coffee-frontend:latest"

echo -e "\n${BLUE}[1/6] Enabling required Google Cloud APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    --project="${GCP_PROJECT}"

echo -e "\n${BLUE}[2/6] Ensuring Artifact Registry repository exists...${NC}"
gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${GCP_REGION}" \
    --description="Docker repository for Optima Coffee services" \
    --project="${GCP_PROJECT}" 2>/dev/null || echo "Repository ${REPO_NAME} already exists."

echo -e "\n${BLUE}[3/6] Building Backend Container with Cloud Build...${NC}"
gcloud builds submit . \
    --project="${GCP_PROJECT}" \
    --config=deploy/cloudbuild-backend.yaml \
    --substitutions=_IMAGE="${BACKEND_IMG}"

echo -e "\n${BLUE}[4/6] Deploying Backend to Cloud Run...${NC}"
JWT_SECRET="${SECRET_KEY:-$(openssl rand -hex 32 2>/dev/null || echo 'production-super-secret-key-32chars-min')}"

gcloud run deploy optima-coffee-backend \
    --image="${BACKEND_IMG}" \
    --region="${GCP_REGION}" \
    --allow-unauthenticated \
    --port=8000 \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --set-env-vars="DATABASE_URL=${DATABASE_URL},SECRET_KEY=${JWT_SECRET},ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=60,ENVIRONMENT=production,BACKEND_CORS_ORIGINS=*" \
    --project="${GCP_PROJECT}"

BACKEND_URL="$(gcloud run services describe optima-coffee-backend --region="${GCP_REGION}" --project="${GCP_PROJECT}" --format='value(status.url)')"
echo -e "${GREEN}✓ Backend successfully deployed at:${NC} ${BACKEND_URL}"

echo -e "\n${BLUE}[5/6] Preparing Frontend configuration and building container...${NC}"
cat <<EOF > frontend/config.js
// Runtime environment configuration generated during Cloud Run deployment
window.__APP_CONFIG__ = window.__APP_CONFIG__ || {
  API_BASE_URL: "${BACKEND_URL}/api/v1",
};
EOF

gcloud builds submit . \
    --project="${GCP_PROJECT}" \
    --config=deploy/cloudbuild-frontend.yaml \
    --substitutions=_IMAGE="${FRONTEND_IMG}"

echo -e "\n${BLUE}[6/6] Deploying Frontend to Cloud Run & Updating CORS...${NC}"
gcloud run deploy optima-coffee-frontend \
    --image="${FRONTEND_IMG}" \
    --region="${GCP_REGION}" \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --memory=256Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --project="${GCP_PROJECT}"

FRONTEND_URL="$(gcloud run services describe optima-coffee-frontend --region="${GCP_REGION}" --project="${GCP_PROJECT}" --format='value(status.url)')"

# Update Backend CORS origins to frontend URL for security
echo "Locking down Backend CORS to Frontend URL..."
gcloud run services update optima-coffee-backend \
    --region="${GCP_REGION}" \
    --update-env-vars="BACKEND_CORS_ORIGINS=${FRONTEND_URL},http://localhost:3000" \
    --project="${GCP_PROJECT}"

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}  ✓ DEPLOYMENT SUCCESSFUL!                                       ${NC}"
echo -e "${GREEN}=================================================================${NC}"
echo -e "Frontend SPA Web Client : ${BLUE}${FRONTEND_URL}${NC}"
echo -e "Backend API Root        : ${BLUE}${BACKEND_URL}${NC}"
echo -e "Interactive Swagger UI  : ${BLUE}${BACKEND_URL}/api/v1/docs${NC}"
echo -e "Health Check Endpoint   : ${BLUE}${BACKEND_URL}/health${NC}"
echo -e "${GREEN}=================================================================${NC}"
