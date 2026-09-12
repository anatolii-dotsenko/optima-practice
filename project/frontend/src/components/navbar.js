/**
 * Navigation Bar Component.
 */
import { api } from "../api/client.js";

export function renderNavbar(activeRoute = "menu") {
  const isAuth = api.isAuthenticated();
  const cartCount = api.getCartCount();

  return `
    <nav class="navbar">
      <a href="#/menu" class="nav-brand">
        ☕ <span>Кав'ярня «Optima Roast»</span>
      </a>
      <div class="nav-links">
        <a href="#/menu" class="nav-link ${activeRoute === "menu" ? "active" : ""}">Меню</a>
        <a href="#/cart" class="nav-link ${activeRoute === "cart" ? "active" : ""}">
          🛒 Кошик <span class="cart-badge" id="nav-cart-badge">${cartCount}</span>
        </a>
        ${
          isAuth
            ? `
          ${
            api.isAdmin()
              ? `<a href="#/admin" class="nav-link ${activeRoute === "admin" ? "active" : ""}">⚙️ Адмін-панель</a>`
              : ""
          }
          <a href="#/profile" class="nav-link ${activeRoute === "profile" ? "active" : ""}">Мій Профіль</a>
          <button id="nav-logout-btn" class="nav-link" style="background:none;border:none;cursor:pointer;">Вийти</button>
        `
            : `
          <a href="#/login" class="nav-link ${activeRoute === "login" ? "active" : ""}">Вхід</a>
          <a href="#/register" class="nav-link ${activeRoute === "register" ? "active" : ""}">Реєстрація</a>
        `
        }
      </div>
    </nav>
  `;
}
