/**
 * Profile and Dashboard Page Component.
 * Demonstrates loading, success, empty, and error states.
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
    const user = await api.getMe();

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
        <h3 style="font-family: var(--font-family-display); font-size: var(--font-size-lg); margin-bottom: var(--space-3);">Історія замовлень</h3>
        <div class="state-alert empty">
          <span>☕ У вас поки немає збережених замовлень. Меню буде доступне у наступному спринті!</span>
        </div>
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
