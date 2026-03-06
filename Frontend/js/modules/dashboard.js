import { AnalyticsAPI, OrderAPI, AuthAPI } from "../api.js";

export function initDashboard() {
  window.loadDashboard = async function () {
    console.log("Loading dashboard...");

    const user = AuthAPI.getCurrentUser();
    if (!user) {
      showToast("Please login first");
      return;
    }

    try {
      // Load user stats
      await loadUserStats(user.id);

      // Load order history
      await loadOrderHistory(user.id);

      // Load analytics (admin)
      if (user.role === "admin") {
        await loadAdminAnalytics();
      }
    } catch (error) {
      console.error("Dashboard load error:", error);
    }
  };

  async function loadUserStats(userId) {
    try {
      const statsEl = document.getElementById("userStats");
      if (!statsEl) return;

      statsEl.innerHTML = "<div class='loading'>Loading stats...</div>";

      // Get order history to calculate stats
      const orderHistory = await OrderAPI.getOrderHistory(userId);

      if (orderHistory.status === "success" && orderHistory.data) {
        const orders = orderHistory.data;
        const totalOrders = orders.length;
        const totalSpent = orders.reduce((sum, o) => sum + (o.total_price || 0), 0);

        statsEl.innerHTML = `
          <div class="stat-card">
            <h3>Total Orders</h3>
            <p class="stat-value">${totalOrders}</p>
          </div>
          <div class="stat-card">
            <h3>Total Spent</h3>
            <p class="stat-value">€${totalSpent.toFixed(2)}</p>
          </div>
        `;
      }
    } catch (error) {
      console.error("Stats error:", error);
    }
  }

  async function loadOrderHistory(userId) {
    try {
      const historyEl = document.getElementById("orderHistory");
      if (!historyEl) return;

      historyEl.innerHTML = "<div class='loading'>Loading orders...</div>";

      const response = await OrderAPI.getOrderHistory(userId);

      if (response.status === "success" && response.data) {
        const orders = response.data;

        if (orders.length === 0) {
          historyEl.innerHTML = "<p>No orders yet</p>";
          return;
        }

        historyEl.innerHTML = `
          <table class="orders-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Medicine</th>
                <th>Quantity</th>
                <th>Total Price</th>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${orders
                .map(
                  (o) => `
                <tr>
                  <td>#${o.id}</td>
                  <td>${o.product_name}</td>
                  <td>${o.quantity}</td>
                  <td>€${o.total_price?.toFixed(2) || "0.00"}</td>
                  <td>${new Date(o.purchase_date).toLocaleDateString()}</td>
                  <td><span class="badge">${o.status || "Completed"}</span></td>
                </tr>
              `
                )
                .join("")}
            </tbody>
          </table>
        `;
      } else {
        historyEl.innerHTML = "<p>Failed to load orders</p>";
      }
    } catch (error) {
      console.error("Order history error:", error);
      const historyEl = document.getElementById("orderHistory");
      if (historyEl) {
        historyEl.innerHTML = "<p>Error loading orders</p>";
      }
    }
  }

  async function loadAdminAnalytics() {
    try {
      const analyticsEl = document.getElementById("adminAnalytics");
      if (!analyticsEl) return;

      analyticsEl.innerHTML = "<div class='loading'>Loading analytics...</div>";

      const dashboard = await AnalyticsAPI.getDashboardStats();
      const salesData = await AnalyticsAPI.getMedicineSalesData();

      if (dashboard.status === "success") {
        const stats = dashboard.data;

        analyticsEl.innerHTML = `
          <div class="analytics-grid">
            <div class="stat-card">
              <h3>Total Revenue</h3>
              <p class="stat-value">€${stats.total_revenue?.toFixed(2) || "0.00"}</p>
            </div>
            <div class="stat-card">
              <h3>Total Orders</h3>
              <p class="stat-value">${stats.total_orders || 0}</p>
            </div>
            <div class="stat-card">
              <h3>Total Customers</h3>
              <p class="stat-value">${stats.total_customers || 0}</p>
            </div>
            <div class="stat-card">
              <h3>Pending Prescriptions</h3>
              <p class="stat-value">${stats.pending_prescriptions || 0}</p>
            </div>
          </div>
        `;

        // Initialize chart if Chart.js is available
        if (window.Chart && salesData.status === "success") {
          renderSalesChart(salesData.data);
        }
      }
    } catch (error) {
      console.error("Analytics error:", error);
    }
  }

  function renderSalesChart(data) {
    const chartCanvas = document.getElementById("salesChart");
    if (!chartCanvas) return;

    const labels = data.map((d) => d.medicine_name);
    const values = data.map((d) => d.total_sales);

    new Chart(chartCanvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Sales (€)",
            data: values,
            backgroundColor: "rgba(75, 192, 192, 0.6)",
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  // Load dashboard on init
  console.log("Dashboard initialized");
}
