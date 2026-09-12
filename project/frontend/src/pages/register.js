/**
 * Registration Page Component with explicit Loading, Error, and Success states.
 */
import { api } from "../api/client.js";

export function renderRegisterPage() {
  return `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-header">
          <h1 class="auth-title">Створити акаунт</h1>
          <p class="auth-subtitle">Приєднуйтесь для швидкого замовлення улюбленої кави</p>
        </div>

        <div id="register-alert-container"></div>

        <form id="register-form" novalidate>
          <div class="form-group">
            <label class="form-label" for="reg-name">Повне ім'я</label>
            <input
              type="text"
              id="reg-name"
              class="form-input"
              placeholder="Оксана Петренко"
              required
              minlength="2"
              autocomplete="name"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="reg-email">Електронна пошта</label>
            <input
              type="email"
              id="reg-email"
              class="form-input"
              placeholder="you@example.com"
              required
              autocomplete="email"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="reg-password">Пароль</label>
            <input
              type="password"
              id="reg-password"
              class="form-input"
              placeholder="Мінімум 8 символів (букви + цифри)"
              required
              minlength="8"
              autocomplete="new-password"
            />
            <p class="form-helper">Пароль повинен містити не менше 8 символів, літери та хоча б одну цифру.</p>
          </div>

          <button type="submit" id="reg-submit-btn" class="btn btn-primary">
            <span class="btn-text">Зареєструватися</span>
          </button>
        </form>

        <div style="text-align: center; margin-top: var(--space-6); font-size: var(--font-size-sm);">
          Вже маєте акаунт? <a href="#/login" style="color: var(--color-brand-accent); font-weight: 600; text-decoration: none;">Увійти</a>
        </div>
      </div>
    </div>
  `;
}

export function initRegisterEvents(navigate) {
  const form = document.getElementById("register-form");
  const alertContainer = document.getElementById("register-alert-container");
  const submitBtn = document.getElementById("reg-submit-btn");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fullName = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;

    // Client-side quick check
    if (!fullName || !email || !password) {
      alertContainer.innerHTML = `
        <div class="state-alert error">
          <span>⚠️ Будь ласка, заповніть усі обов'язкові поля.</span>
        </div>
      `;
      return;
    }

    // Set Loading State
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<div class="spinner"></div><span>Створення акаунта...</span>`;
    alertContainer.innerHTML = "";

    try {
      await api.register({
        full_name: fullName,
        email: email,
        password: password,
      });

      // Set Success State
      alertContainer.innerHTML = `
        <div class="state-alert success">
          <span>✅ Реєстрація успішна! Перенаправляємо на сторінку входу...</span>
        </div>
      `;

      setTimeout(() => {
        navigate("login");
      }, 1500);
    } catch (err) {
      // Set Error State
      let errorMessage = err.message;
      if (err.status === 409) {
        errorMessage = "Користувач із такою електронною поштою вже зареєстрований.";
      } else if (err.status === 422) {
        errorMessage = "Помилка валідації: перевірте правильність email та надійність пароля.";
      }

      alertContainer.innerHTML = `
        <div class="state-alert error">
          <span>❌ ${errorMessage}</span>
        </div>
      `;

      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span class="btn-text">Зареєструватися</span>`;
    }
  });
}
