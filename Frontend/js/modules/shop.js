import { InventoryAPI, PrescriptionAPI } from "../api.js";
import { cartItems } from "../state.js";

export function initShop() {
  window.renderShopGrid = async function () {
    const grid = document.getElementById("shopGrid");

    if (!grid) return;

    // Show loading state
    grid.innerHTML = '<div class="loading">Loading medicines...</div>';

    try {
      // Fetch medicines from API
      const medicinesData = await InventoryAPI.getAllMedicines();

      if (medicinesData.status === "error" || !medicinesData.data) {
        grid.innerHTML =
          '<div class="error">Failed to load medicines. Please try again.</div>';
        return;
      }

      const medicines = medicinesData.data;

      grid.innerHTML = medicines
        .map(
          (m) => `
        <div class="card" data-medicine-id="${m.id}">
          <h4>${m.name}</h4>
          <p class="price">€${m.price}</p>
          <p class="stock">Stock: ${m.stock}</p>
          ${m.prescription_required === "Yes" ? '<span class="badge">Requires Rx</span>' : ""}
          <button onclick="addToCartFromAPI(${m.id}, '${m.name}', ${m.price})">
            Add to Cart
          </button>
        </div>
      `
        )
        .join("");
    } catch (error) {
      console.error("Error loading medicines:", error);
      grid.innerHTML =
        '<div class="error">Error loading medicines. Please refresh.</div>';
    }
  };

  // Updated add to cart function
  window.addToCartFromAPI = function (medicineId, name, price) {
    const existing = cartItems.find((i) => i.id === medicineId);

    if (existing) {
      existing.qty++;
    } else {
      cartItems.push({ id: medicineId, name, price, qty: 1 });
    }

    renderCart();
    showToast(`${name} added to cart`);
  };

  window.renderCart = function () {
    const el = document.getElementById("cartItems");

    if (!el) return;

    if (cartItems.length === 0) {
      el.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
      return;
    }

    const total = cartItems.reduce((sum, item) => sum + item.price * item.qty, 0);

    el.innerHTML = `
      <div class="cart-list">
        ${cartItems
          .map(
            (c, i) => `
          <div class="cart-item">
            <div>
              <strong>${c.name}</strong>
              <p>€${c.price} x ${c.qty}</p>
            </div>
            <button onclick="removeCartItem(${i})" class="btn-remove">Remove</button>
          </div>
        `
          )
          .join("")}
      </div>
      <div class="cart-total">
        <strong>Total: €${total.toFixed(2)}</strong>
      </div>
    `;
  };

  window.removeCartItem = function (i) {
    const item = cartItems[i];
    cartItems.splice(i, 1);
    renderCart();
    showToast(`${item.name} removed from cart`);
  };

  // Search functionality
  window.searchMedicines = async function () {
    const searchInput = document.getElementById("searchInput");
    const query = searchInput.value.trim();

    if (!query) {
      renderShopGrid();
      return;
    }

    const grid = document.getElementById("shopGrid");
    grid.innerHTML = '<div class="loading">Searching...</div>';

    try {
      const results = await InventoryAPI.searchMedicines(query);
      
      if (results.status === "error" || !results.data) {
        grid.innerHTML = `<div class="error">No medicines found for "${query}"</div>`;
        return;
      }

      const medicines = results.data;
      grid.innerHTML = medicines
        .map(
          (m) => `
        <div class="card" data-medicine-id="${m.id}">
          <h4>${m.name}</h4>
          <p class="price">€${m.price}</p>
          <p class="stock">Stock: ${m.stock}</p>
          ${m.prescription_required === "Yes" ? '<span class="badge">Requires Rx</span>' : ""}
          <button onclick="addToCartFromAPI(${m.id}, '${m.name}', ${m.price})">
            Add to Cart
          </button>
        </div>
      `
        )
        .join("");
    } catch (error) {
      console.error("Search error:", error);
      grid.innerHTML = '<div class="error">Search failed. Please try again.</div>';
    }
  };

  // Initialize shop on load
  renderShopGrid();
}
