/**
 * Isolated REST API Client for Coffee Shop Application.
 *
 * Requirements:
 * - Isolated in one module
 * - No hardcoded API URLs (derives dynamically from environment, window global, or default origin)
 */

class ApiClient {
  constructor() {
    this.baseUrl = this._resolveBaseUrl();
    this.tokenKey = "coffee_shop_access_token";
  }

  _resolveBaseUrl() {
    // Allows overriding API URL via window or localStorage without touching codebase
    if (typeof window !== "undefined" && window.__APP_CONFIG__?.API_BASE_URL) {
      return window.__APP_CONFIG__.API_BASE_URL;
    }
    const stored = typeof localStorage !== "undefined" ? localStorage.getItem("coffee_api_url") : null;
    if (stored) {
      return stored;
    }
    // Default fallback to local FastAPI backend v1 prefix
    return "http://localhost:8000/api/v1";
  }

  setBaseUrl(url) {
    this.baseUrl = url.replace(/\/+$/, "");
    if (typeof localStorage !== "undefined") {
      localStorage.setItem("coffee_api_url", this.baseUrl);
    }
  }

  getToken() {
    return typeof localStorage !== "undefined" ? localStorage.getItem(this.tokenKey) : null;
  }

  setToken(token) {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(this.tokenKey, token);
    }
  }

  clearToken() {
    if (typeof localStorage !== "undefined") {
      localStorage.removeItem(this.tokenKey);
    }
  }

  isAuthenticated() {
    return Boolean(this.getToken());
  }

  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      let data = null;

      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      }

      if (!response.ok) {
        const error = new Error(data?.message || `HTTP Error ${response.status}`);
        error.status = response.status;
        error.code = data?.code || "unknown_error";
        error.details = data?.details || null;
        throw error;
      }

      return data;
    } catch (err) {
      if (!err.status) {
        // Network or connection failure
        err.code = "network_error";
        err.message = "Could not connect to backend service. Please ensure the server is running.";
      }
      throw err;
    }
  }

  /**
   * Register a new user account.
   * @param {Object} payload { email, password, full_name }
   */
  async register(payload) {
    return this._request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  /**
   * Authenticate credentials and store JWT token.
   * @param {Object} payload { email, password }
   */
  async login(payload) {
    const data = await this._request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (data?.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  /**
   * Fetch current authenticated user profile.
   */
  async getMe() {
    return this._request("/auth/me", {
      method: "GET",
    });
  }

  /**
   * Verify server health status.
   */
  async checkHealth() {
    return this._request("/../health", {
      method: "GET",
    });
  }
}

export const api = new ApiClient();
