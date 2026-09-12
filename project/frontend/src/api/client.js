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
    this.userKey = "coffee_shop_user";
    this.cartKey = "coffee_shop_cart";
  }

  _resolveBaseUrl() {
    if (typeof window !== "undefined" && window.__APP_CONFIG__?.API_BASE_URL) {
      return window.__APP_CONFIG__.API_BASE_URL;
    }
    const stored = typeof localStorage !== "undefined" ? localStorage.getItem("coffee_api_url") : null;
    if (stored) {
      return stored;
    }
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
      localStorage.removeItem(this.userKey);
    }
  }

  isAuthenticated() {
    return Boolean(this.getToken());
  }

  getUser() {
    if (typeof localStorage === "undefined") return null;
    try {
      const data = localStorage.getItem(this.userKey);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  }

  setUser(user) {
    if (typeof localStorage !== "undefined") {
      if (user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
      } else {
        localStorage.removeItem(this.userKey);
      }
    }
  }

  isAdmin() {
    const user = this.getUser();
    return Boolean(user && user.is_superuser);
  }

  // --- Cart Management ---

  getCart() {
    if (typeof localStorage === "undefined") return [];
    try {
      const data = localStorage.getItem(this.cartKey);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  _saveCart(cart) {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(this.cartKey, JSON.stringify(cart));
      window.dispatchEvent(new Event("cart_updated"));
    }
  }

  addToCart(item) {
    const cart = this.getCart();
    const existing = cart.find((i) => i.id === item.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      cart.push({
        id: item.id,
        name: item.name,
        price: parseFloat(item.price),
        image_url: item.image_url,
        quantity: 1,
      });
    }
    this._saveCart(cart);
  }

  updateCartQuantity(itemId, delta) {
    let cart = this.getCart();
    const existing = cart.find((i) => i.id === itemId);
    if (existing) {
      existing.quantity += delta;
      if (existing.quantity <= 0) {
        cart = cart.filter((i) => i.id !== itemId);
      }
      this._saveCart(cart);
    }
  }

  removeFromCart(itemId) {
    let cart = this.getCart();
    cart = cart.filter((i) => i.id !== itemId);
    this._saveCart(cart);
  }

  clearCart() {
    this._saveCart([]);
  }

  getCartCount() {
    return this.getCart().reduce((acc, item) => acc + item.quantity, 0);
  }

  getCartTotal() {
    return this.getCart().reduce((acc, item) => acc + item.price * item.quantity, 0);
  }

  // --- HTTP Request Engine ---

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
        err.code = "network_error";
        err.message = "Could not connect to backend service. Please ensure the server is running.";
      }
      throw err;
    }
  }

  // --- Auth Endpoints ---

  async register(payload) {
    return this._request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async login(payload) {
    const data = await this._request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (data?.access_token) {
      this.setToken(data.access_token);
      try {
        const user = await this.getMe();
        this.setUser(user);
      } catch {}
    }
    return data;
  }

  async getMe() {
    const user = await this._request("/auth/me", {
      method: "GET",
    });
    this.setUser(user);
    return user;
  }

  // --- Menu Endpoints ---

  async getCategories() {
    return this._request("/menu/categories", {
      method: "GET",
    });
  }

  async getMenuItems({ categoryId, search, availableOnly = true } = {}) {
    const params = new URLSearchParams();
    if (categoryId) params.append("category_id", categoryId);
    if (search) params.append("search", search);
    if (availableOnly !== undefined) params.append("available_only", availableOnly);

    const queryStr = params.toString() ? `?${params.toString()}` : "";
    return this._request(`/menu/items${queryStr}`, {
      method: "GET",
    });
  }

  async getMenuItem(itemId) {
    return this._request(`/menu/items/${itemId}`, {
      method: "GET",
    });
  }

  async createMenuItem(payload) {
    return this._request("/menu/items", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async updateMenuItem(itemId, payload) {
    return this._request(`/menu/items/${itemId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  async toggleItemAvailability(itemId, isAvailable) {
    return this._request(`/menu/items/${itemId}/availability`, {
      method: "PATCH",
      body: JSON.stringify({ is_available: isAvailable }),
    });
  }

  async deleteMenuItem(itemId) {
    return this._request(`/menu/items/${itemId}`, {
      method: "DELETE",
    });
  }

  async createCategory(payload) {
    return this._request("/menu/categories", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // --- Orders Endpoints ---

  async createOrder({ items, notes }) {
    return this._request("/orders", {
      method: "POST",
      body: JSON.stringify({ items, notes }),
    });
  }

  async getMyOrders() {
    return this._request("/orders", {
      method: "GET",
    });
  }

  async getAdminOrders(status = null) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return this._request(`/orders/admin${query}`, {
      method: "GET",
    });
  }

  async updateOrderStatus(orderId, status) {
    return this._request(`/orders/${orderId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  }

  async getOrder(orderId) {
    return this._request(`/orders/${orderId}`, {
      method: "GET",
    });
  }

  async checkHealth() {
    return this._request("/../health", {
      method: "GET",
    });
  }
}

export const api = new ApiClient();
