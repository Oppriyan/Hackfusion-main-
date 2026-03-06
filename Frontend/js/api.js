// ============================================================
// PHARMLY API CLIENT
// ============================================================
// Base configuration for all API calls

const API_BASE = "http://localhost:5000";

// Helper for consistent error handling
function handleApiError(error) {
  console.error("API Error:", error);
  return {
    status: "error",
    message: error.message || "API request failed",
  };
}

// Helper for API requests
async function apiCall(method, endpoint, body = null) {
  try {
    const options = {
      method: method,
      headers: {
        "Content-Type":
          body instanceof FormData ? undefined : "application/json",
      },
    };

    if (body && !(body instanceof FormData)) {
      options.body = JSON.stringify(body);
    } else if (body instanceof FormData) {
      options.body = body;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);

    // Handle non-JSON responses
    const contentType = response.headers.get("content-type");
    let data;

    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    return {
      ok: response.ok,
      status: response.status,
      data: data,
    };
  } catch (error) {
    return handleApiError(error);
  }
}

// ============================================================
// AUTHENTICATION APIs
// ============================================================

export const AuthAPI = {
  login: async (email, password) => {
    const response = await apiCall("POST", "/auth/login", { email, password });
    if (response.ok) {
      localStorage.setItem("auth_token", response.data.token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
      return response.data;
    }
    return response.data || { error: "Login failed" };
  },

  register: async (name, email, password) => {
    const response = await apiCall("POST", "/auth/register", {
      name,
      email,
      password,
    });
    return response.data || { error: "Registration failed" };
  },

  logout: () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");
    return { status: "success" };
  },

  getCurrentUser: () => {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },
};

// ============================================================
// INVENTORY APIs
// ============================================================

export const InventoryAPI = {
  getAllMedicines: async () => {
    const response = await apiCall("GET", "/inventory/medicines");
    return response.data || { error: "Failed to fetch medicines" };
  },

  getMedicineById: async (medicineId) => {
    const response = await apiCall("GET", `/inventory/medicine/${medicineId}`);
    return response.data || { error: "Medicine not found" };
  },

  searchMedicines: async (query) => {
    const response = await apiCall("GET", `/inventory/search?q=${query}`);
    return response.data || { error: "Search failed" };
  },

  getMedicineStock: async (medicineId) => {
    const response = await apiCall("GET", `/inventory/stock/${medicineId}`);
    return response.data || { error: "Failed to fetch stock" };
  },

  checkMedicineRequiresPrescription: async (medicineId) => {
    const response = await apiCall(
      "GET",
      `/prescription/medicine-requires-prescription/${medicineId}`
    );
    return response.data || { error: "Failed to check prescription requirement" };
  },
};

// ============================================================
// ORDER APIs
// ============================================================

export const OrderAPI = {
  createOrder: async (customerId, medicineId, quantity = 1) => {
    const response = await apiCall("POST", "/create-order", {
      customer_id: customerId,
      medicine_id: medicineId,
      quantity: quantity,
    });
    return response.data || { error: "Order creation failed" };
  },

  getOrderHistory: async (customerId) => {
    const response = await apiCall("GET", `/customer-history/${customerId}`);
    return response.data || { error: "Failed to fetch order history" };
  },

  cancelOrder: async (orderId, customerId) => {
    const response = await apiCall("POST", "/cancel-order", {
      order_id: orderId,
      customer_id: customerId,
    });
    return response.data || { error: "Order cancellation failed" };
  },

  getOrderDetails: async (orderId) => {
    const response = await apiCall("GET", `/order-status/${orderId}`);
    return response.data || { error: "Failed to fetch order details" };
  },
};

// ============================================================
// PRESCRIPTION APIs
// ============================================================

export const PrescriptionAPI = {
  uploadPrescription: async (customerId, medicineId, file) => {
    const formData = new FormData();
    formData.append("customer_id", customerId);
    formData.append("medicine_id", medicineId);
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/prescription/upload-prescription`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      return data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  checkPrescriptionStatus: async (customerId, medicineId) => {
    const response = await apiCall("POST", "/prescription/check-prescription", {
      customer_id: customerId,
      medicine_id: medicineId,
    });
    return response.data || { error: "Failed to check prescription status" };
  },

  approvePrescription: async (customerId, medicineId, approve = true) => {
    const response = await apiCall("POST", "/prescription/approve-prescription", {
      customer_id: customerId,
      medicine_id: medicineId,
      approve: approve,
    });
    return response.data || { error: "Approval operation failed" };
  },

  getPendingPrescriptions: async () => {
    const response = await apiCall("GET", "/prescription/pending-prescriptions");
    return response.data || { error: "Failed to fetch pending prescriptions" };
  },

  rejectPrescription: async (customerId, medicineId) => {
    const response = await apiCall("POST", "/prescription/approve-prescription", {
      customer_id: customerId,
      medicine_id: medicineId,
      approve: false,
    });
    return response.data || { error: "Rejection failed" };
  },
};

// ============================================================
// CHAT / AGENT APIs
// ============================================================

export const ChatAPI = {
  sendMessage: async (message, customerId = "PAT999") => {
    const response = await apiCall("POST", "/chat/message", {
      message: message,
      customer_id: customerId,
    });
    return response.data || { error: "Failed to send message" };
  },

  getConversationHistory: async (customerId = "PAT999") => {
    const response = await apiCall("POST", "/chat/history", {
      customer_id: customerId,
    });
    return response.data || { error: "Failed to fetch conversation" };
  },

  sendVoiceMessage: async (message, customerId = "PAT999", callId = null) => {
    const response = await apiCall("POST", "/chat/voice-webhook", {
      message: message,
      customer_id: customerId,
      call_id: callId,
    });
    return response.data || { error: "Failed to process voice message" };
  },
};

// ============================================================
// ANALYTICS APIs
// ============================================================

export const AnalyticsAPI = {
  getDashboardStats: async () => {
    const response = await apiCall("GET", "/analytics/dashboard");
    return response.data || { error: "Failed to fetch analytics" };
  },

  getMedicineSalesData: async () => {
    const response = await apiCall("GET", "/analytics/medicine-sales");
    return response.data || { error: "Failed to fetch sales data" };
  },

  getOrderAnalytics: async () => {
    const response = await apiCall("GET", "/analytics/orders");
    return response.data || { error: "Failed to fetch order analytics" };
  },

  getPrescriptionAnalytics: async () => {
    const response = await apiCall("GET", "/analytics/prescriptions");
    return response.data || { error: "Failed to fetch prescription analytics" };
  },
};

// ============================================================
// CHECKOUT / PAYMENT APIs
// ============================================================

export const CheckoutAPI = {
  validateCart: async (cartItems, customerId) => {
    const response = await apiCall("POST", "/checkout/validate", {
      items: cartItems,
      customer_id: customerId,
    });
    return response.data || { error: "Cart validation failed" };
  },

  processCheckout: async (cartItems, customerId, paymentMethod) => {
    const response = await apiCall("POST", "/checkout/process", {
      items: cartItems,
      customer_id: customerId,
      payment_method: paymentMethod,
    });
    return response.data || { error: "Checkout failed" };
  },

  getCheckoutSummary: async (cartItems, customerId) => {
    const response = await apiCall("POST", "/checkout/summary", {
      items: cartItems,
      customer_id: customerId,
    });
    return response.data || { error: "Failed to calculate summary" };
  },
};

// ============================================================
// UTILITY FUNCTIONS FOR FRONTEND
// ============================================================

// Transaction wrapper for better error handling
export async function withErrorHandling(apiCall, errorHandler = null) {
  try {
    return await apiCall();
  } catch (error) {
    console.error("Transaction error:", error);
    if (errorHandler) {
      errorHandler(error);
    }
    return null;
  }
}

// Show loading state and call API
export async function apiWithLoading(apiCall, loadingElement = null) {
  if (loadingElement) {
    loadingElement.style.display = "block";
  }

  try {
    const result = await apiCall();
    return result;
  } finally {
    if (loadingElement) {
      loadingElement.style.display = "none";
    }
  }
}

// Check if user is logged in
export function isUserLoggedIn() {
  return localStorage.getItem("auth_token") !== null;
}

// Get stored auth token
export function getAuthToken() {
  return localStorage.getItem("auth_token");
}

// ============================================================
// INITIALIZE API ERROR INTERCEPTOR
// ============================================================

// Add global error handler for all API calls
window.addEventListener("fetch", (event) => {
  // This is a browser-level interceptor for advanced scenarios
  // For now, errors are handled at the apiCall level
});
