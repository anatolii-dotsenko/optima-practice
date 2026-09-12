/**
 * Admin & Barista Dashboard Page.
 *
 * Provides:
 * 1. Menu Catalog Management (Add item, edit price/details, toggle stop-list, delete item).
 * 2. Barista Order Queue (Live orders, status transitions according to ADR-0006).
 */
import { api } from "../api/client.js";

let currentTab = "menu"; // "menu" | "orders"
let catalogItems = [];
let catalogCategories = [];
let orderQueue = [];
let selectedOrderFilter = "all";
let editingItem = null;

export function renderAdminPage() {
  const isAuth = api.isAuthenticated();
  const isAdmin = api.isAdmin();

  if (!isAuth) {
    return `
      <div class="auth-card" style="margin-top: 40px;">
        <div class="auth-header">
          <div class="auth-icon">🔒</div>
          <h1 class="auth-title">Вхід для персоналу</h1>
          <p class="auth-desc">Будь ласка, увійдіть з обліковим записом адміністратора або бариста.</p>
        </div>
        <div style="text-align: center; margin-top: 20px;">
          <a href="#/login" class="btn btn-primary">Перейти до входу</a>
        </div>
      </div>
    `;
  }

  if (!isAdmin) {
    return `
      <div class="state-alert error" style="margin-top: 40px; max-width: 600px; margin-left: auto; margin-right: auto;">
        <h3>⛔ Доступ обмежено</h3>
        <p>Цей розділ доступний виключно для персоналу кав'ярні з правами адміністратора.</p>
        <div style="margin-top: 15px;">
          <a href="#/menu" class="btn btn-secondary">Повернутися до меню</a>
        </div>
      </div>
    `;
  }

  return `
    <div class="admin-dashboard-container">
      <div class="admin-header">
        <div>
          <h1 class="admin-title">⚙️ Панель управління «Optima Roast»</h1>
          <p class="admin-subtitle">Керування каталогом меню, стоп-листом та живою чергою замовлень</p>
        </div>
        <div class="admin-header-badge">
          <span class="badge-role">Адміністратор</span>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="admin-tabs">
        <button class="admin-tab-btn ${currentTab === "menu" ? "active" : ""}" id="tab-btn-menu">
          📋 Меню та Стоп-лист
        </button>
        <button class="admin-tab-btn ${currentTab === "orders" ? "active" : ""}" id="tab-btn-orders">
          ☕ Черга замовлень бариста <span class="tab-counter" id="orders-pending-counter">0</span>
        </button>
      </div>

      <!-- Tab 1: Menu Catalog Management -->
      <div id="admin-menu-view" style="${currentTab === "menu" ? "display:block;" : "display:none;"}">
        <div class="admin-toolbar">
          <div class="admin-search-box">
            <input type="text" id="admin-menu-search" class="form-input" placeholder="Пошук страви або напою..." />
            <select id="admin-category-filter" class="form-input" style="max-width: 220px;">
              <option value="">Всі категорії</option>
            </select>
          </div>
          <button class="btn btn-primary" id="btn-open-add-item-modal">
            + Додати позицію
          </button>
        </div>

        <div id="admin-items-table-container">
          <div class="state-alert info">Завантаження каталогу...</div>
        </div>
      </div>

      <!-- Tab 2: Barista Orders Queue -->
      <div id="admin-orders-view" style="${currentTab === "orders" ? "display:block;" : "display:none;"}">
        <div class="orders-toolbar">
          <div class="order-filter-chips">
            <button class="filter-chip ${selectedOrderFilter === "all" ? "active" : ""}" data-order-filter="all">Всі замовлення</button>
            <button class="filter-chip ${selectedOrderFilter === "pending" ? "active" : ""}" data-order-filter="pending">Очікують підтвердження</button>
            <button class="filter-chip ${selectedOrderFilter === "confirmed" ? "active" : ""}" data-order-filter="confirmed">Готуються</button>
            <button class="filter-chip ${selectedOrderFilter === "ready" ? "active" : ""}" data-order-filter="ready">Готові до видачі</button>
            <button class="filter-chip ${selectedOrderFilter === "completed" ? "active" : ""}" data-order-filter="completed">Видані</button>
          </div>
          <button class="btn btn-secondary btn-sm" id="btn-refresh-orders">
            🔄 Оновити чергу
          </button>
        </div>

        <div id="admin-orders-board">
          <div class="state-alert info">Завантаження замовлень...</div>
        </div>
      </div>
    </div>

    <!-- Modal for Add/Edit Menu Item -->
    <div id="item-modal-overlay" class="modal-overlay" style="display:none;">
      <div class="modal-card">
        <div class="modal-header">
          <h2 id="modal-item-title">Додати позицію меню</h2>
          <button class="modal-close-btn" id="btn-close-modal">✕</button>
        </div>
        <form id="item-form" class="modal-form">
          <div class="form-group">
            <label class="form-label" for="item-name">Назва страви / напою *</label>
            <input type="text" id="item-name" class="form-input" required placeholder="напр., Флет Вайт" />
          </div>

          <div class="form-row">
            <div class="form-group" style="flex:1;">
              <label class="form-label" for="item-category">Категорія *</label>
              <select id="item-category" class="form-input" required></select>
            </div>
            <div class="form-group" style="flex:1;">
              <label class="form-label" for="item-price">Ціна (₴) *</label>
              <input type="number" step="0.50" min="1" id="item-price" class="form-input" required placeholder="75.00" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="item-desc">Опис та інгредієнти</label>
            <textarea id="item-desc" class="form-input" rows="3" placeholder="Свіжообсмажена кава, подвійний шот еспресо..."></textarea>
          </div>

          <div class="form-group">
            <label class="form-label" for="item-image">URL фотографії</label>
            <input type="url" id="item-image" class="form-input" placeholder="https://images.unsplash.com/..." />
          </div>

          <div class="form-group" style="display:flex;align-items:center;gap:10px;">
            <input type="checkbox" id="item-available" checked style="width:18px;height:18px;cursor:pointer;" />
            <label for="item-available" style="cursor:pointer;font-weight:600;">Позиція в наявності (доступна до замовлення)</label>
          </div>

          <div id="modal-error-alert" class="state-alert error" style="display:none;margin-top:10px;"></div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" id="btn-cancel-modal">Скасувати</button>
            <button type="submit" class="btn btn-primary" id="btn-save-item">Зберегти</button>
          </div>
        </form>
      </div>
    </div>
  `;
}

async function loadCategories() {
  try {
    catalogCategories = await api.getCategories();
    const filterSelect = document.getElementById("admin-category-filter");
    const modalSelect = document.getElementById("item-category");

    if (filterSelect) {
      filterSelect.innerHTML = `<option value="">Всі категорії</option>` +
        catalogCategories.map((c) => `<option value="${c.id}">${c.name}</option>`).join("");
    }
    if (modalSelect) {
      modalSelect.innerHTML = catalogCategories.map((c) => `<option value="${c.id}">${c.name}</option>`).join("");
    }
  } catch (err) {
    console.error("Failed to load categories:", err);
  }
}

async function loadCatalogItems() {
  const container = document.getElementById("admin-items-table-container");
  if (!container) return;

  const filterCat = document.getElementById("admin-category-filter")?.value;
  const searchVal = document.getElementById("admin-menu-search")?.value;

  try {
    container.innerHTML = `<div class="state-alert info">Оновлення каталогу...</div>`;
    catalogItems = await api.getMenuItems({
      categoryId: filterCat ? parseInt(filterCat, 10) : undefined,
      search: searchVal || undefined,
      availableOnly: false, // Admin sees both available and unavailable
    });

    if (!catalogItems || catalogItems.length === 0) {
      container.innerHTML = `
        <div class="state-alert info">
          Позицій не знайдено за заданими критеріями.
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="table-responsive">
        <table class="admin-table">
          <thead>
            <tr>
              <th style="width: 60px;">Фото</th>
              <th>Назва та опис</th>
              <th>Категорія</th>
              <th>Ціна</th>
              <th>Статус наявності</th>
              <th style="text-align: right;">Дії</th>
            </tr>
          </thead>
          <tbody>
            ${catalogItems
              .map((item) => {
                const cat = catalogCategories.find((c) => c.id === item.category_id);
                return `
                <tr>
                  <td>
                    <div class="admin-thumb">
                      ${
                        item.image_url
                          ? `<img src="${item.image_url}" alt="${item.name}" onerror="this.parentElement.innerHTML='☕'" />`
                          : `☕`
                      }
                    </div>
                  </td>
                  <td>
                    <div class="admin-item-title">${item.name}</div>
                    <div class="admin-item-desc">${item.description || "—"}</div>
                  </td>
                  <td>
                    <span class="category-tag">${cat?.name || "Категорія #" + item.category_id}</span>
                  </td>
                  <td>
                    <span class="admin-item-price">${parseFloat(item.price).toFixed(2)} ₴</span>
                  </td>
                  <td>
                    <button
                      class="btn-toggle-stock ${item.is_available ? "in-stock" : "out-of-stock"}"
                      data-toggle-id="${item.id}"
                      data-current-available="${item.is_available}"
                      title="Клікніть, щоб змінити наявність"
                    >
                      ${item.is_available ? "✓ В наявності" : "✕ Стоп-лист"}
                    </button>
                  </td>
                  <td style="text-align: right;">
                    <div class="table-actions">
                      <button class="btn btn-secondary btn-sm" data-edit-id="${item.id}">Редагувати</button>
                      <button class="btn btn-danger btn-sm" data-delete-id="${item.id}">Видалити</button>
                    </div>
                  </td>
                </tr>
              `;
              })
              .join("")}
          </tbody>
        </table>
      </div>
    `;

    // Attach row event listeners
    attachCatalogRowListeners(container);
  } catch (err) {
    container.innerHTML = `
      <div class="state-alert error">
        Помилка завантаження каталогу: ${err.message}
      </div>
    `;
  }
}

function attachCatalogRowListeners(container) {
  // Toggle availability
  container.querySelectorAll("[data-toggle-id]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = parseInt(btn.getAttribute("data-toggle-id"), 10);
      const currentAvail = btn.getAttribute("data-current-available") === "true";
      try {
        btn.disabled = true;
        await api.toggleItemAvailability(id, !currentAvail);
        await loadCatalogItems();
      } catch (err) {
        alert("Не вдалося змінити статус наявності: " + err.message);
        btn.disabled = false;
      }
    });
  });

  // Edit item
  container.querySelectorAll("[data-edit-id]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.getAttribute("data-edit-id"), 10);
      const item = catalogItems.find((i) => i.id === id);
      if (item) {
        openEditItemModal(item);
      }
    });
  });

  // Delete item
  container.querySelectorAll("[data-delete-id]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = parseInt(btn.getAttribute("data-delete-id"), 10);
      const item = catalogItems.find((i) => i.id === id);
      if (item && confirm(`Ви дійсно бажаєте видалити "${item.name}" з меню?`)) {
        try {
          await api.deleteMenuItem(id);
          await loadCatalogItems();
        } catch (err) {
          alert("Не вдалося видалити позицію: " + err.message);
        }
      }
    });
  });
}

function openAddItemModal() {
  editingItem = null;
  document.getElementById("modal-item-title").textContent = "Додати нову позицію";
  document.getElementById("item-name").value = "";
  document.getElementById("item-price").value = "";
  document.getElementById("item-desc").value = "";
  document.getElementById("item-image").value = "";
  document.getElementById("item-available").checked = true;
  document.getElementById("modal-error-alert").style.display = "none";
  document.getElementById("item-modal-overlay").style.display = "flex";
}

function openEditItemModal(item) {
  editingItem = item;
  document.getElementById("modal-item-title").textContent = "Редагувати: " + item.name;
  document.getElementById("item-name").value = item.name;
  document.getElementById("item-category").value = item.category_id;
  document.getElementById("item-price").value = parseFloat(item.price).toFixed(2);
  document.getElementById("item-desc").value = item.description || "";
  document.getElementById("item-image").value = item.image_url || "";
  document.getElementById("item-available").checked = item.is_available;
  document.getElementById("modal-error-alert").style.display = "none";
  document.getElementById("item-modal-overlay").style.display = "flex";
}

function closeItemModal() {
  document.getElementById("item-modal-overlay").style.display = "none";
  editingItem = null;
}

async function loadOrderQueue() {
  const board = document.getElementById("admin-orders-board");
  if (!board) return;

  try {
    board.innerHTML = `<div class="state-alert info">Оновлення черги...</div>`;
    const filterStatus = selectedOrderFilter === "all" ? null : selectedOrderFilter;
    orderQueue = await api.getAdminOrders(filterStatus);

    // Update pending counter
    const pendingCount = orderQueue.filter((o) => o.status === "pending").length;
    const badgeEl = document.getElementById("orders-pending-counter");
    if (badgeEl) badgeEl.textContent = pendingCount;

    if (!orderQueue || orderQueue.length === 0) {
      board.innerHTML = `
        <div class="state-alert info" style="text-align:center;padding:40px;">
          <h3>Немає замовлень у цій категорії</h3>
          <p>Всі замовлення опрацьовано або нові ще не надходили.</p>
        </div>
      `;
      return;
    }

    board.innerHTML = `
      <div class="orders-grid">
        ${orderQueue
          .map((ord) => {
            const dateStr = new Date(ord.created_at).toLocaleTimeString("uk-UA", {
              hour: "2-digit",
              minute: "2-digit",
            });
            const statusConfig = getStatusBadgeConfig(ord.status);

            return `
            <div class="admin-order-card" data-order-card="${ord.id}">
              <div class="admin-order-header">
                <div>
                  <span class="admin-order-id">Замовлення #${ord.id}</span>
                  <span class="admin-order-time">⏰ ${dateStr}</span>
                </div>
                <span class="status-badge ${statusConfig.className}">
                  ${statusConfig.label}
                </span>
              </div>

              <div class="admin-order-customer">
                👤 <strong>${ord.customer_name || "Клієнт"}</strong> (${ord.customer_email || "user #" + ord.user_id})
              </div>

              <div class="admin-order-items">
                ${ord.items
                  .map(
                    (it) => `
                  <div class="admin-order-item-row">
                    <span>${it.item_name} × <strong>${it.quantity}</strong></span>
                    <span>${(parseFloat(it.unit_price) * it.quantity).toFixed(2)} ₴</span>
                  </div>
                `
                  )
                  .join("")}
              </div>

              ${
                ord.notes
                  ? `<div class="admin-order-notes">💬 Коментар: <em>"${ord.notes}"</em></div>`
                  : ""
              }

              <div class="admin-order-footer">
                <div class="admin-order-total">
                  Разом: <strong>${parseFloat(ord.total_amount).toFixed(2)} ₴</strong>
                </div>
                <div class="admin-order-actions">
                  ${renderOrderActionButtons(ord)}
                </div>
              </div>
            </div>
          `;
          })
          .join("")}
      </div>
    `;

    attachOrderActionListeners(board);
  } catch (err) {
    board.innerHTML = `
      <div class="state-alert error">
        Помилка завантаження черги: ${err.message}
      </div>
    `;
  }
}

function getStatusBadgeConfig(status) {
  switch (status) {
    case "pending":
      return { label: "Очікує", className: "badge-pending" };
    case "confirmed":
      return { label: "Готується", className: "badge-confirmed" };
    case "ready":
      return { label: "Готово до видачі", className: "badge-ready" };
    case "completed":
      return { label: "Видано ✓", className: "badge-completed" };
    case "cancelled":
      return { label: "Скасовано ✕", className: "badge-cancelled" };
    default:
      return { label: status, className: "" };
  }
}

function renderOrderActionButtons(order) {
  if (order.status === "pending") {
    return `
      <button class="btn btn-success btn-sm" data-order-action="confirmed" data-id="${order.id}">
        ✓ Прийняти в роботу
      </button>
      <button class="btn btn-danger btn-sm" data-order-action="cancelled" data-id="${order.id}">
        ✕ Скасувати
      </button>
    `;
  }
  if (order.status === "confirmed") {
    return `
      <button class="btn btn-primary btn-sm" data-order-action="ready" data-id="${order.id}">
        ☕ Готово до видачі
      </button>
      <button class="btn btn-danger btn-sm" data-order-action="cancelled" data-id="${order.id}">
        ✕ Скасувати
      </button>
    `;
  }
  if (order.status === "ready") {
    return `
      <button class="btn btn-success btn-sm" data-order-action="completed" data-id="${order.id}">
        🛍️ Видати замовлення
      </button>
    `;
  }
  return `<span class="text-muted" style="font-size:0.85rem;">Замовлення завершено</span>`;
}

function attachOrderActionListeners(board) {
  board.querySelectorAll("[data-order-action]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = parseInt(btn.getAttribute("data-id"), 10);
      const targetStatus = btn.getAttribute("data-order-action");
      try {
        btn.disabled = true;
        await api.updateOrderStatus(id, targetStatus);
        await loadOrderQueue();
      } catch (err) {
        alert("Помилка зміни статусу: " + err.message);
        btn.disabled = false;
      }
    });
  });
}

export async function initAdminEvents() {
  if (!api.isAuthenticated() || !api.isAdmin()) return;

  // Tabs switching
  const tabMenu = document.getElementById("tab-btn-menu");
  const tabOrders = document.getElementById("tab-btn-orders");
  const viewMenu = document.getElementById("admin-menu-view");
  const viewOrders = document.getElementById("admin-orders-view");

  tabMenu?.addEventListener("click", () => {
    currentTab = "menu";
    tabMenu.classList.add("active");
    tabOrders.classList.remove("active");
    viewMenu.style.display = "block";
    viewOrders.style.display = "none";
    loadCatalogItems();
  });

  tabOrders?.addEventListener("click", () => {
    currentTab = "orders";
    tabOrders.classList.add("active");
    tabMenu.classList.remove("active");
    viewOrders.style.display = "block";
    viewMenu.style.display = "none";
    loadOrderQueue();
  });

  // Modal controls
  document.getElementById("btn-open-add-item-modal")?.addEventListener("click", openAddItemModal);
  document.getElementById("btn-close-modal")?.addEventListener("click", closeItemModal);
  document.getElementById("btn-cancel-modal")?.addEventListener("click", closeItemModal);

  // Form submit (Add or Edit item)
  document.getElementById("item-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("item-name").value.trim();
    const categoryId = parseInt(document.getElementById("item-category").value, 10);
    const price = parseFloat(document.getElementById("item-price").value);
    const description = document.getElementById("item-desc").value.trim();
    const imageUrl = document.getElementById("item-image").value.trim();
    const isAvailable = document.getElementById("item-available").checked;

    const errorAlert = document.getElementById("modal-error-alert");
    const saveBtn = document.getElementById("btn-save-item");

    try {
      saveBtn.disabled = true;
      errorAlert.style.display = "none";

      const payload = {
        name,
        category_id: categoryId,
        price: price.toFixed(2),
        description: description || null,
        image_url: imageUrl || null,
        is_available: isAvailable,
      };

      if (editingItem) {
        await api.updateMenuItem(editingItem.id, payload);
      } else {
        await api.createMenuItem(payload);
      }

      closeItemModal();
      await loadCatalogItems();
    } catch (err) {
      errorAlert.textContent = err.message || "Помилка збереження позиції";
      errorAlert.style.display = "block";
    } finally {
      saveBtn.disabled = false;
    }
  });

  // Catalog filters
  let debounceTimeout = null;
  document.getElementById("admin-menu-search")?.addEventListener("input", () => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(loadCatalogItems, 300);
  });

  document.getElementById("admin-category-filter")?.addEventListener("change", loadCatalogItems);

  // Orders filters
  document.querySelectorAll("[data-order-filter]").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll("[data-order-filter]").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      selectedOrderFilter = chip.getAttribute("data-order-filter");
      loadOrderQueue();
    });
  });

  document.getElementById("btn-refresh-orders")?.addEventListener("click", loadOrderQueue);

  // Initial load
  await loadCategories();
  if (currentTab === "menu") {
    await loadCatalogItems();
  } else {
    await loadOrderQueue();
  }
}
