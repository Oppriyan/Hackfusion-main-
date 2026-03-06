import { cartItems } from "../state.js";

export function initCart() {
  window.addToCart = function (name, price) {
    const existing = cartItems.find((i) => i.name === name);

    if (existing) {
      existing.qty++;
    } else {
      cartItems.push({ name, price, qty: 1 });
    }

    renderCart();
  };

  window.renderCart = function () {
    const el = document.getElementById("cartItems");

    if (!el) return;

    if (cartItems.length === 0) {
      el.innerHTML = "<p>Your cart is empty</p>";
      return;
    }

    const total = cartItems.reduce((sum, item) => sum + item.price * item.qty, 0);

    el.innerHTML = `
      ${cartItems
        .map(
          (c, i) => `
        <div class="cart-item">
          <span>${c.name} x${c.qty}</span>
          <span>€${(c.price * c.qty).toFixed(2)}</span>
          <button onclick="removeCartItem(${i})">Remove</button>
        </div>
      `
        )
        .join("")}
      <div class="cart-total">
        <strong>Total: €${total.toFixed(2)}</strong>
      </div>
    `;
  };

  window.removeCartItem = function (i) {
    cartItems.splice(i, 1);
    renderCart();
  };

  window.toggleCart = function () {
    const cartDrop = document.getElementById("cartDrop");
    if (cartDrop) {
      cartDrop.classList.toggle("show");
    }
  };

  window.clearCart = function () {
    if (confirm("Clear cart?")) {
      cartItems.length = 0;
      renderCart();
    }
  };

  window.openCheckout = async function () {
    if (cartItems.length === 0) {
      showToast("Your cart is empty");
      return;
    }
    openModal("checkoutModal");
  };
}
