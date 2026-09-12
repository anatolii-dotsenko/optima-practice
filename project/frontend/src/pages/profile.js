/**
 * Profile and Dashboard Page Component.
 * Demonstrates dynamic order history with state badges and loading/empty/error states.
 */
import { api } from "../api/client.js";

export function renderProfilePage() {
  return `
    <div id="profile-content" class="profile-card">
      <div style="text-align: center; padding: var(--space-8);">
        <div class="spinner" style="margin: 0 auto; border-top-color: var(--color-brand-primary);"></div>
        <p style="margin-top: var(--space-4); color: var(--color-text-secondary);">Завантаження даних профілю...</p>
      </div>
    </div>
  `;
}

export async function initProfileEvents(navigate) {
  const container = document.getElementById("profile-content");
  if (!container) return;

  try {
    const [user, orders] = await Promise.all([
      api.getMe(),
      api.getMyOrders().catch(() => []),
    ]);

    const initials = user.full_name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);

    const memberSince = new Date(user.created_at).toLocaleDateString("uk-UA", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    const statusMap = {
      pending: { label: "Очікує підтвердження", cls: "status-pending" },
      confirmed: { label: "Готується", cls: "status-confirmed" },
      ready: { label: "Готово до видачі", cls: "status-ready" },
      completed: { label: "Видано", cls: "status-completed" },
      cancelled: { label: "Скасовано", cls: "status-cancelled" },
    };

    const ordersHtml =
      orders && orders.length > 0
        ? `
        <div class="orders-list">
          ${orders
            .map((order) => {
              const orderDate = new Date(order.created_at).toLocaleString("uk-UA", {
                day: "numeric",
                month: "short",
                hour: "2-digit",
                minute: "2-digit",
              });
              const statusInfo = statusMap[order.status.toLowerCase()] || {
                label: order.status,
                cls: "status-pending",
              };

              return `
              <div class="order-card">
                <div class="order-card-header">
                  <div>
                    <strong style="color: var(--color-brand-primary);">Замовлення #${order.id}</strong>
                    <div class="order-card-date">${orderDate}</div>
                  </div>
                  <span class="order-badge ${statusInfo.cls}">${statusInfo.label}</span>
                </div>

                <div class="order-card-items">
                  ${order.items
                    .map(
                      (item) => `
                    <div>• <strong>${item.item_name}</strong> × ${item.quantity} (${parseFloat(item.unit_price * item.quantity).toFixed(2)} ₴)</div>
                  `
                    )
                    .join("")}
                  ${order.notes ? `<div style="font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: var(--space-1); font-style: italic;">Коментар: ${order.notes}</div>` : ""}
                </div>

                <div class="order-card-footer">
                  <span style="color: var(--color-text-secondary);">Сума замовлення:</span>
                  <span style="color: var(--color-brand-accent-dark); font-size: var(--font-size-base);">${parseFloat(order.total_amount).toFixed(2)} ₴</span>
                </div>
              </div>
            `;
            })
            .join("")}
        </div>
      `
        : `
        <div class="state-alert empty">
          <span>☕ У вас поки немає замовлень. <a href="#/menu" style="color: var(--color-brand-primary); font-weight: 600;">Перегляньте меню</a>, щоб зробити перше передзамовлення!</span>
        </div>
      `;

    container.innerHTML = `
      <div class="profile-header">
        <div class="avatar-badge">${initials}</div>
        <div>
          <h2 style="font-family: var(--font-family-display); font-size: var(--font-size-2xl);">${user.full_name}</h2>
          <p style="color: var(--color-text-secondary); font-size: var(--font-size-sm);">${user.email}</p>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin-bottom: var(--space-6);">
        <div style="background: var(--color-bg-muted); padding: var(--space-4); border-radius: var(--radius-md);">
          <span style="font-size: var(--font-size-xs); color: var(--color-text-muted); display: block;">СТАТУС АКАУНТА</span>
          <span class="badge-active">● Активний</span>
        </div>
        <div style="background: var(--color-bg-muted); padding: var(--space-4); border-radius: var(--radius-md);">
          <span style="font-size: var(--font-size-xs); color: var(--color-text-muted); display: block;">ДАТА РЕЄСТРАЦІЇ</span>
          <span style="font-weight: 600; font-size: var(--font-size-sm);">${memberSince}</span>
        </div>
      </div>

      <div style="margin-bottom: var(--space-6);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-3);">
          <h3 style="font-family: var(--font-family-display); font-size: var(--font-size-lg);">Історія замовлень</h3>
          <a href="#/menu" class="nav-link" style="font-size: var(--font-size-xs); font-weight: 600;">+ Нове замовлення</a>
        </div>
        ${ordersHtml}
      </div>

      <div style="display: flex; gap: var(--space-4);">
        <button id="profile-logout-btn" class="btn btn-outline">Вийти з акаунта</button>
      </div>
    `;

    document.getElementById("profile-logout-btn")?.addEventListener("click", () => {
      api.clearToken();
      navigate("login");
    });
  } catch (err) {
    container.innerHTML = `
      <div class="state-alert error">
        <span>❌ Не вдалося завантажити профіль: ${err.message}</span>
      </div>
      <button id="profile-retry-btn" class="btn btn-primary" style="margin-top: var(--space-4);">Увійти знову</button>
    `;

    document.getElementById("profile-retry-btn")?.addEventListener("click", () => {
      api.clearToken();
      navigate("login");
    });
  }
}
