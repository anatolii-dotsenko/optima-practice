/**
 * Main application router and initializer.
 */
import { api } from "./api/client.js";
import { renderNavbar } from "./components/navbar.js";
import { initCartEvents, renderCartPage } from "./pages/cart.js";
import { initLoginEvents, renderLoginPage } from "./pages/login.js";
import { initMenuEvents, renderMenuPage } from "./pages/menu.js";
import { initProfileEvents, renderProfilePage } from "./pages/profile.js";
import { initRegisterEvents, renderRegisterPage } from "./pages/register.js";

const routes = {
  menu: { render: renderMenuPage, init: initMenuEvents },
  cart: { render: renderCartPage, init: initCartEvents },
  login: { render: renderLoginPage, init: initLoginEvents },
  register: { render: renderRegisterPage, init: initRegisterEvents },
  profile: { render: renderProfilePage, init: initProfileEvents },
};

function getRouteFromHash() {
  const hash = window.location.hash.replace(/^#\/?/, "") || "menu";
  return routes[hash] ? hash : "menu";
}

export function navigate(route) {
  window.location.hash = `#/${route}`;
}

function updateCartBadge() {
  const badge = document.getElementById("nav-cart-badge");
  if (badge) {
    badge.textContent = api.getCartCount();
  }
}

function renderApp() {
  const activeRoute = getRouteFromHash();
  const appElement = document.getElementById("app");

  if (!appElement) return;

  appElement.innerHTML = `
    ${renderNavbar(activeRoute)}
    <main class="app-container">
      ${routes[activeRoute].render()}
    </main>
  `;

  // Attach navbar logout listener
  document.getElementById("nav-logout-btn")?.addEventListener("click", () => {
    api.clearToken();
    navigate("login");
  });

  // Initialize page-specific events
  routes[activeRoute].init(navigate);
}

window.addEventListener("hashchange", renderApp);
window.addEventListener("DOMContentLoaded", renderApp);
window.addEventListener("cart_updated", updateCartBadge);
