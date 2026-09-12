/**
 * Cart and Pre-order Checkout Page Component.
 * Supports item quantity adjustment, special barista notes, and server-authoritative checkout.
 * Explicit states: loading, success, empty, error.
 */
import { api } from "../api/client.js";

export function renderCartPage() {
  return `
    <div id="cart-content">
      <div style="text-align: center; padding: var(--space-8);">
        <div class="spinner" style="margin: 0 auto; border-top-color: var(--color-brand-primary);"></div>
        <p style="margin-top: var(--space-4); color: var(--color-text-secondary);">Завантаження кошика...</p>
      </div>
    </div>
  `;
}

export function initCartEvents(navigate) {
  const container = document.getElementById("cart-content");
  if (!container) return;

  function renderView() {
    const cart = api.getCart();
    const isAuth = api.isAuthenticated();

    if (!cart || cart.length === 0) {
      container.innerHTML = `
        <div class="cart-items-card" style="text-align: center; padding: var(--space-12) var(--space-6); max-width: 600px; margin: 0 auto;">
          <span style="font-size: 3.5rem; display: block; margin-bottom: var(--space-3);">🛒</span>
          <h2 style="font-family: var(--font-family-display); font-size: var(--font-size-2xl); font-weight: bold; margin-bottom: var(--space-2); color: var(--color-brand-primary);">
            Ваш кошик порожній
          </h2>
          <p style="color: var(--color-text-secondary); margin-bottom: var(--space-6);">
            Додайте улюблену каву або свіжу випічку, щоб оформити швидке передзамовлення.
          </p>
          <a href="#/menu" class="btn btn-primary" style="display: inline-flex; width: auto; padding: var(--space-3) var(--space-6);">
            Переглянути меню
          </a>
        </div>
      `;
      return;
    }

    const total = api.getCartTotal();
    const count = api.getCartCount();

    container.innerHTML = `
      <h1 style="font-family: var(--font-family-display); font-size: var(--font-size-3xl); font-weight: var(--font-weight-bold); color: var(--color-brand-primary); margin-bottom: var(--space-6);">
        Оформлення передзамовлення
      </h1>

      <div id="cart-alert"></div>

      <div class="cart-container">
        <!-- Cart Items List -->
        <div class="cart-items-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); border-bottom: var(--border-subtle); padding-bottom: var(--space-3);">
            <h2 style="font-family: var(--font-family-display); font-size: var(--font-size-lg);">
              Вибрані позиції (${count})
            </h2>
            <button id="clear-cart-btn" class="btn-outline" style="border: none; color: var(--color-state-error-text); cursor: pointer; font-size: var(--font-size-xs); padding: var(--space-1);">
              Очистити все
            </button>
          </div>

          <div class="cart-items-list">
            ${cart
              .map(
                (item) => `
              <div class="cart-item" data-cart-item-id="${item.id}">
                <div class="cart-item-info">
                  <div class="cart-item-name">${item.name}</div>
                  <div class="cart-item-price">${parseFloat(item.price).toFixed(2)} ₴ / шт.</div>
                </div>
                <div class="cart-qty-controls">
                  <button class="btn-qty" data-action="dec" data-id="${item.id}">−</button>
                  <span class="cart-qty-val">${item.quantity}</span>
                  <button class="btn-qty" data-action="inc" data-id="${item.id}">+</button>
                </div>
                <div class="cart-item-total">
                  ${(item.price * item.quantity).toFixed(2)} ₴
                </div>
                <button class="btn-remove-item" data-action="remove" data-id="${item.id}" title="Видалити">
                  ✕
                </button>
              </div>
            `
              )
              .join("")}
          </div>
        </div>

        <!-- Checkout Summary -->
        <div class="cart-summary-card">
          <h2 style="font-family: var(--font-family-display); font-size: var(--font-size-lg); margin-bottom: var(--space-4);">
            Разом до сплати
          </h2>

          <div class="cart-summary-row">
            <span>Вартість товарів:</span>
            <span>${total.toFixed(2)} ₴</span>
          </div>
          <div class="cart-summary-row">
            <span>Знижка:</span>
            <span>0.00 ₴</span>
          </div>

          <div class="cart-summary-total">
            <span>До сплати:</span>
            <span>${total.toFixed(2)} ₴</span>
          </div>

          <div class="form-group">
            <label class="form-label" for="order-notes">Побажання баристі (опціонально):</label>
            <textarea
              id="order-notes"
              class="form-input"
              rows="2"
              placeholder="Наприклад: вівсяне молоко, без цукру, буду за 10 хв..."
              style="resize: vertical;"
            ></textarea>
          </div>

          ${
            !isAuth
              ? `
            <div class="state-alert empty" style="font-size: var(--font-size-xs); margin-bottom: var(--space-4);">
              <span>Для оформлення замовлення, будь ласка, увійдіть в акаунт.</span>
            </div>
            <button id="cart-login-btn" class="btn btn-outline" style="margin-bottom: var(--space-2);">
              Увійти в акаунт
            </button>
          `
              : `
            <button id="checkout-btn" class="btn btn-primary">
              <span id="checkout-btn-text">Підтвердити передзамовлення</span>
              <div id="checkout-spinner" class="spinner" style="display: none;"></div>
            </button>
          `
          }
        </div>
      </div>
    `;

    // Quantity listeners
    container.querySelectorAll("[data-action='inc']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-id"), 10);
        api.updateCartQuantity(id, 1);
        renderView();
      });
    });

    container.querySelectorAll("[data-action='dec']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-id"), 10);
        api.updateCartQuantity(id, -1);
        renderView();
      });
    });

    container.querySelectorAll("[data-action='remove']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-id"), 10);
        api.removeFromCart(id);
        renderView();
      });
    });

    document.getElementById("clear-cart-btn")?.addEventListener("click", () => {
      api.clearCart();
      renderView();
    });

    document.getElementById("cart-login-btn")?.addEventListener("click", () => {
      navigate("login");
    });

    // Checkout submit listener
    const checkoutBtn = document.getElementById("checkout-btn");
    const checkoutBtnText = document.getElementById("checkout-btn-text");
    const checkoutSpinner = document.getElementById("checkout-spinner");
    const alertBox = document.getElementById("cart-alert");

    checkoutBtn?.addEventListener("click", async () => {
      checkoutBtn.disabled = true;
      if (checkoutBtnText) checkoutBtnText.style.display = "none";
      if (checkoutSpinner) checkoutSpinner.style.display = "block";
      alertBox.innerHTML = "";

      const notes = document.getElementById("order-notes")?.value?.trim() || null;
      const payloadItems = cart.map((i) => ({
        menu_item_id: i.id,
        quantity: i.quantity,
      }));

      try {
        const order = await api.createOrder({
          items: payloadItems,
          notes,
        });

        // Clear cart after successful checkout
        api.clearCart();

        container.innerHTML = `
          <div class="cart-items-card" style="text-align: center; padding: var(--space-12) var(--space-6); max-width: 600px; margin: 0 auto;">
            <span style="font-size: 3.5rem; display: block; margin-bottom: var(--space-3);">🎉</span>
            <h2 style="font-family: var(--font-family-display); font-size: var(--font-size-2xl); font-weight: bold; color: var(--color-brand-primary); margin-bottom: var(--space-2);">
              Замовлення успішно створено!
            </h2>
            <p style="color: var(--color-text-secondary); margin-bottom: var(--space-2);">
              Номер вашого замовлення: <strong>#${order.id}</strong>
            </p>
            <p style="color: var(--color-text-secondary); margin-bottom: var(--space-6);">
              Сума: <strong>${parseFloat(order.total_amount).toFixed(2)} ₴</strong> • Статус:
              <span class="order-badge status-pending" style="vertical-align: middle;">Очікує</span>
            </p>
            <p style="font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-6);">
              Бариста вже отримав ваше замовлення та розпочинає приготування.
            </p>
            <div style="display: flex; gap: var(--space-4); justify-content: center; flex-wrap: wrap;">
              <a href="#/profile" class="btn btn-primary" style="width: auto; padding: var(--space-3) var(--space-6);">
                Переглянути статус у Профілі
              </a>
              <a href="#/menu" class="btn btn-outline" style="width: auto; padding: var(--space-3) var(--space-6);">
                Повернутися до меню
              </a>
            </div>
          </div>
        `;
      } catch (err) {
        checkoutBtn.disabled = false;
        if (checkoutBtnText) checkoutBtnText.style.display = "inline";
        if (checkoutSpinner) checkoutSpinner.style.display = "none";

        alertBox.innerHTML = `
          <div class="state-alert error">
            <span>❌ Не вдалося оформити замовлення: ${err.message}</span>
          </div>
        `;
      }
    });
  }

  renderView();
}
