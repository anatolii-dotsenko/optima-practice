// Runtime environment configuration for Optima Coffee Web Client
window.__APP_CONFIG__ = window.__APP_CONFIG__ || {
  // By default, uses local backend on port 8000.
  // When deploying to Google Cloud Run, update this URL to your Cloud Run backend URL:
  // e.g.: "https://optima-coffee-backend-xxxxxx.a.run.app/api/v1"
  API_BASE_URL: "http://localhost:8000/api/v1",
};
