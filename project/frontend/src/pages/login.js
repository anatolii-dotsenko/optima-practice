/**
 * Login Page Component with explicit Loading, Error, and Success states.
 */
import { api } from "../api/client.js";

export function renderLoginPage() {
  return `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-header">
          <h1 class="auth-title">Вхід до системи</h1>
          <p class="auth-subtitle">Введіть свої облікові дані для доступу до меню та замовлень</p>
        </div>

        <div id="login-alert-container"></div>

        <form id="login-form" novalidate>
          <div class="form-group">
            <label class="form-label" for="login-email">Електронна пошта</label>
            <input
              type="email"
              id="login-email"
              class="form-input"
              placeholder="you@example.com"
              required
              autocomplete="email"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="login-password">Пароль</label>
            <input
              type="password"
              id="login-password"
              class="form-input"
              placeholder="Ваш пароль"
              required
              autocomplete="current-password"
            />
          </div>

          <button type="submit" id="login-submit-btn" class="btn btn-primary">
            <span class="btn-text">Увійти</span>
          </button>
        </form>

        <div style="margin-top: var(--space-5); padding: var(--space-4); background: rgba(184, 115, 51, 0.08); border: 1px dashed var(--color-brand-accent); border-radius: var(--radius-md);">
          <div style="font-weight: 600; font-size: var(--font-size-sm); margin-bottom: var(--space-2); color: var(--color-brand-primary);">
            ⚡ Швидкий демо-доступ:
          </div>
          <div style="display: flex; gap: var(--space-2); margin-bottom: var(--space-2);">
            <button type="button" id="btn-fill-barista" class="btn btn-secondary" style="flex: 1; font-size: var(--font-size-xs); padding: 0.4rem;">
              ☕ Бариста
            </button>
            <button type="button" id="btn-fill-customer" class="btn btn-secondary" style="flex: 1; font-size: var(--font-size-xs); padding: 0.4rem;">
              👤 Клієнт
            </button>
          </div>
          <div style="font-size: var(--font-size-xs); color: var(--color-text-secondary); line-height: 1.4;">
            Бариста: <code>barista@optima.coffee</code> (пароль: <code>barista123</code>)<br/>
            Клієнт: <code>customer@optima.coffee</code> (пароль: <code>customer123</code>)
          </div>
        </div>

        <div style="text-align: center; margin-top: var(--space-5); font-size: var(--font-size-sm);">
          Ще не зареєстровані? <a href="#/register" style="color: var(--color-brand-accent); font-weight: 600; text-decoration: none;">Створити акаунт</a>
        </div>
      </div>
    </div>
  `;
}

export function initLoginEvents(navigate) {
  const form = document.getElementById("login-form");
  const alertContainer = document.getElementById("login-alert-container");
  const submitBtn = document.getElementById("login-submit-btn");

  // Autofill helpers for demo users
  document.getElementById("btn-fill-barista")?.addEventListener("click", () => {
    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    if (emailInput && passwordInput) {
      emailInput.value = "barista@optima.coffee";
      passwordInput.value = "barista123";
    }
  });

  document.getElementById("btn-fill-customer")?.addEventListener("click", () => {
    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    if (emailInput && passwordInput) {
      emailInput.value = "customer@optima.coffee";
      passwordInput.value = "customer123";
    }
  });

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    if (!email || !password) {
      alertContainer.innerHTML = `
        <div class="state-alert error">
          <span>⚠️ Будь ласка, введіть email та пароль.</span>
        </div>
      `;
      return;
    }

    // Set Loading State
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<div class="spinner"></div><span>Перевірка даних...</span>`;
    alertContainer.innerHTML = "";

    try {
      await api.login({ email, password });

      // Set Success State
      alertContainer.innerHTML = `
        <div class="state-alert success">
          <span>✅ Успішний вхід! Завантаження профілю...</span>
        </div>
      `;

      setTimeout(() => {
        if (api.isAdmin()) {
          navigate("admin");
        } else {
          navigate("profile");
        }
      }, 800);
    } catch (err) {
      // Set Error State
      let errorMessage = err.message;
      if (err.status === 401) {
        errorMessage = "Невірний email або пароль. Будь ласка, спробуйте ще раз.";
      } else if (err.status === 403) {
        errorMessage = "Ваш обліковий запис деактивовано. Зверніться до підтримки.";
      }

      alertContainer.innerHTML = `
        <div class="state-alert error">
          <span>❌ ${errorMessage}</span>
        </div>
      `;

      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span class="btn-text">Увійти</span>`;
    }
  });
}
