/**
 * Navigation Bar Component.
 */
import { api } from "../api/client.js";

export function renderNavbar(activeRoute = "login") {
  const isAuth = api.isAuthenticated();

  return `
    <nav class="navbar">
      <a href="#/menu" class="nav-brand">
        ☕ <span>Кав'ярня «Optima Roast»</span>
      </a>
      <div class="nav-links">
        ${
          isAuth
            ? `
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
