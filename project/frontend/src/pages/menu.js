/**
 * Menu Catalog Page Component.
 * Supports category filtering, search, and inline +/- quantity adjustment on cards.
 * Explicit states: loading, success, empty, error.
 */
import { api } from "../api/client.js";

let currentCategoryId = null;
let currentSearchQuery = "";
let allCategories = [];
let currentItems = [];

export function renderMenuPage() {
  return `
    <div class="menu-header">
      <h1 style="font-family: var(--font-family-display); font-size: var(--font-size-3xl); font-weight: var(--font-weight-bold); color: var(--color-brand-primary); margin-bottom: var(--space-2);">
        Меню кав'ярні
      </h1>
      <p style="color: var(--color-text-secondary); margin-bottom: var(--space-6);">
        Обирайте улюблені напої та свіжу випічку для швидкого онлайн-передзамовлення.
      </p>

      <div class="menu-search-bar">
        <input
          type="text"
          id="menu-search-input"
          class="menu-search-input"
          placeholder="🔍 Пошук за назвою або описом..."
          value="${currentSearchQuery}"
        />
      </div>

      <div class="category-tabs" id="category-tabs">
        <button class="category-tab ${currentCategoryId === null ? "active" : ""}" data-category-id="">
          Всі позиції
        </button>
      </div>
    </div>

    <div id="menu-items-container">
      <div style="text-align: center; padding: var(--space-8);">
        <div class="spinner" style="margin: 0 auto; border-top-color: var(--color-brand-primary);"></div>
        <p style="margin-top: var(--space-4); color: var(--color-text-secondary);">Завантаження меню...</p>
      </div>
    </div>
  `;
}

function getCategoryFallback(categoryId) {
  const cat = allCategories.find((c) => c.id === categoryId);
  const slug = cat?.slug || "";
  if (slug === "bakery") return "🥐";
  if (slug === "desserts") return "🍰";
  if (slug === "tea") return "🍵";
  return "☕";
}

function renderCardAction(item) {
  if (!item.is_available) {
    return `<button class="btn btn-primary btn-add-cart" disabled>Недоступно</button>`;
  }

  const cart = api.getCart();
  const cartItem = cart.find((i) => i.id === item.id);
  const qty = cartItem ? cartItem.quantity : 0;

  if (qty > 0) {
    return `
      <div class="menu-card-qty-controls" data-card-controls="${item.id}">
        <button class="btn-qty btn-qty-card" data-card-action="dec" data-id="${item.id}">−</button>
        <span class="cart-qty-val" id="card-qty-${item.id}">${qty}</span>
        <button class="btn-qty btn-qty-card" data-card-action="inc" data-id="${item.id}">+</button>
      </div>
    `;
  }

  return `
    <button class="btn btn-primary btn-add-cart" data-add-id="${item.id}">
      + У кошик
    </button>
  `;
}

function attachCardActionListeners(container) {
  // Add to cart button
  container.querySelectorAll("[data-add-id]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.getAttribute("data-add-id"), 10);
      const item = currentItems.find((i) => i.id === id);
      if (item) {
        api.addToCart(item);
        const actionSlot = container.querySelector(`[data-action-slot="${id}"]`);
        if (actionSlot) {
          actionSlot.innerHTML = renderCardAction(item);
          attachCardActionListeners(actionSlot);
        }
      }
    });
  });

  // Increment button
  container.querySelectorAll("[data-card-action='inc']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.getAttribute("data-id"), 10);
      const item = currentItems.find((i) => i.id === id);
      if (item) {
        api.updateCartQuantity(id, 1);
        const actionSlot = container.querySelector(`[data-action-slot="${id}"]`);
        if (actionSlot) {
          actionSlot.innerHTML = renderCardAction(item);
          attachCardActionListeners(actionSlot);
        }
      }
    });
  });

  // Decrement button
  container.querySelectorAll("[data-card-action='dec']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.getAttribute("data-id"), 10);
      const item = currentItems.find((i) => i.id === id);
      if (item) {
        api.updateCartQuantity(id, -1);
        const actionSlot = container.querySelector(`[data-action-slot="${id}"]`);
        if (actionSlot) {
          actionSlot.innerHTML = renderCardAction(item);
          attachCardActionListeners(actionSlot);
        }
      }
    });
  });
}

function syncAllCardActions() {
  const container = document.getElementById("menu-items-container");
  if (!container || currentItems.length === 0) return;

  currentItems.forEach((item) => {
    const actionSlot = container.querySelector(`[data-action-slot="${item.id}"]`);
    if (actionSlot) {
      actionSlot.innerHTML = renderCardAction(item);
      attachCardActionListeners(actionSlot);
    }
  });
}

async function loadAndRenderItems() {
  const container = document.getElementById("menu-items-container");
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: var(--space-8);">
      <div class="spinner" style="margin: 0 auto; border-top-color: var(--color-brand-primary);"></div>
      <p style="margin-top: var(--space-4); color: var(--color-text-secondary);">Оновлення списку позицій...</p>
    </div>
  `;

  try {
    const items = await api.getMenuItems({
      categoryId: currentCategoryId || undefined,
      search: currentSearchQuery || undefined,
    });
    currentItems = items || [];

    if (!items || items.length === 0) {
      container.innerHTML = `
        <div class="state-alert empty" style="padding: var(--space-8);">
          <div>
            <span style="font-size: 2rem; display: block; margin-bottom: var(--space-2);">☕</span>
            <p style="font-weight: 500;">За вашим запитом нічого не знайдено.</p>
            <p style="font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: var(--space-1);">Спробуйте змінити категорію або параметри пошуку.</p>
          </div>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="menu-grid">
        ${items
          .map((item) => {
            const fallbackEmoji = getCategoryFallback(item.category_id);
            return `
            <div class="menu-card" data-item-id="${item.id}">
              <div class="menu-card-img">
                ${
                  item.image_url
                    ? `<img src="${item.image_url}" alt="${item.name}" style="width:100%;height:100%;object-fit:cover;" onerror="this.parentElement.innerHTML='${fallbackEmoji}'" />`
                    : fallbackEmoji
                }
              </div>
              <div class="menu-card-body">
                <div class="menu-card-title">${item.name}</div>
                <div class="menu-card-desc">${item.description || "Свіжоприготований напій або десерт найвищої якості."}</div>
                <div class="menu-card-footer">
                  <span class="menu-card-price">${parseFloat(item.price).toFixed(2)} ₴</span>
                  <div data-action-slot="${item.id}">
                    ${renderCardAction(item)}
                  </div>
                </div>
              </div>
            </div>
          `;
          })
          .join("")}
      </div>
    `;

    attachCardActionListeners(container);
  } catch (err) {
    container.innerHTML = `
      <div class="state-alert error">
        <span>❌ Помилка завантаження меню: ${err.message}</span>
      </div>
      <button id="menu-retry-btn" class="btn btn-outline" style="max-width: 200px; margin: var(--space-4) auto 0;">Спробувати знову</button>
    `;
    document.getElementById("menu-retry-btn")?.addEventListener("click", loadAndRenderItems);
  }
}

export async function initMenuEvents() {
  const tabsContainer = document.getElementById("category-tabs");
  const searchInput = document.getElementById("menu-search-input");

  // Load categories if not cached
  try {
    allCategories = await api.getCategories();
    if (tabsContainer) {
      tabsContainer.innerHTML = `
        <button class="category-tab ${currentCategoryId === null ? "active" : ""}" data-category-id="">
          Всі позиції
        </button>
        ${allCategories
          .map(
            (cat) => `
          <button class="category-tab ${currentCategoryId === cat.id ? "active" : ""}" data-category-id="${cat.id}">
            ${cat.name}
          </button>
        `
          )
          .join("")}
      `;

      tabsContainer.querySelectorAll(".category-tab").forEach((tab) => {
        tab.addEventListener("click", () => {
          tabsContainer.querySelectorAll(".category-tab").forEach((t) => t.classList.remove("active"));
          tab.classList.add("active");
          const catId = tab.getAttribute("data-category-id");
          currentCategoryId = catId ? parseInt(catId, 10) : null;
          loadAndRenderItems();
        });
      });
    }
  } catch (err) {
    console.error("Failed to load categories", err);
  }

  // Setup search input listener (debounced)
  let debounceTimeout = null;
  searchInput?.addEventListener("input", (e) => {
    currentSearchQuery = e.target.value.trim();
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      loadAndRenderItems();
    }, 300);
  });

  // Listen to cart_updated event to keep cards in sync
  window.addEventListener("cart_updated", syncAllCardActions);

  // Initial items load
  await loadAndRenderItems();
}
