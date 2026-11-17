// Runtime environment configuration for Optima Coffee Web Client
window.__APP_CONFIG__ = window.__APP_CONFIG__ || {
  // If served directly from backend (e.g. AWS EC2, Cloud Run), use relative path
  // so browser connects to the current host and port automatically.
  // When running local dev frontend on port 3000, fall back to localhost:8000:
  API_BASE_URL:
    typeof window !== "undefined" && window.location.port === "3000"
      ? "http://localhost:8000/api/v1"
      : "/api/v1",
};
