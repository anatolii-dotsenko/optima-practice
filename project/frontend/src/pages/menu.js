/**
 * Menu Catalog Page Component.
 * Supports category filtering, search, and adding items to the pre-order cart.
 * Explicit states: loading, success, empty, error.
 */
import { api } from "../api/client.js";

let currentCategoryId = null;
let currentSearchQuery = "";
let allCategories = [];

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
          .map(
            (item) => `
          <div class="menu-card" data-item-id="${item.id}">
            <div class="menu-card-img">
              ${
                item.image_url
                  ? `<img src="${item.image_url}" alt="${item.name}" style="width:100%;height:100%;object-fit:cover;" onerror="this.parentElement.innerHTML='☕'" />`
                  : `☕`
              }
            </div>
            <div class="menu-card-body">
              <div class="menu-card-title">${item.name}</div>
              <div class="menu-card-desc">${item.description || "Свіжоприготований напій або десерт найвищої якості."}</div>
              <div class="menu-card-footer">
                <span class="menu-card-price">${parseFloat(item.price).toFixed(2)} ₴</span>
                <button
                  class="btn btn-primary btn-add-cart"
                  data-add-id="${item.id}"
                  ${!item.is_available ? "disabled" : ""}
                >
                  ${item.is_available ? "+ У кошик" : "Недоступно"}
                </button>
              </div>
            </div>
          </div>
        `
          )
          .join("")}
      </div>
    `;

    // Attach add-to-cart listeners
    container.querySelectorAll("[data-add-id]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-add-id"), 10);
        const item = items.find((i) => i.id === id);
        if (item) {
          api.addToCart(item);
          const origText = btn.textContent;
          btn.textContent = "Додано! ✓";
          btn.style.backgroundColor = "var(--color-state-success-text)";
          setTimeout(() => {
            btn.textContent = origText;
            btn.style.backgroundColor = "";
          }, 800);
        }
      });
    });
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

  // Initial items load
  await loadAndRenderItems();
}
