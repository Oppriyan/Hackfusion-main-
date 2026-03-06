import { AuthAPI } from "../api.js";

export function initAuth() {
  // Login function
  window.loginUser = async function () {
    const email = document.getElementById("loginEmail")?.value || "";
    const password = document.getElementById("loginPassword")?.value || "";

    if (!email || !password) {
      showToast("Please enter email and password");
      return;
    }

    try {
      const result = await AuthAPI.login(email, password);

      if (result.status === "success" || result.token) {
        showToast("Login successful!");
        setTimeout(() => {
          window.location.href = "#dashboard";
        }, 1500);
      } else {
        showToast(result.message || "Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      showToast("Login error. Please try again.");
    }
  };

  // Register function
  window.registerUser = async function () {
    const name = document.getElementById("registerName")?.value || "";
    const email = document.getElementById("registerEmail")?.value || "";
    const password = document.getElementById("registerPassword")?.value || "";
    const confirmPassword = document.getElementById("confirmPassword")?.value || "";

    // Validation
    if (!name || !email || !password) {
      showToast("Please fill all fields");
      return;
    }

    if (password !== confirmPassword) {
      showToast("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      showToast("Password must be at least 6 characters");
      return;
    }

    try {
      const result = await AuthAPI.register(name, email, password);

      if (result.status === "success") {
        showToast("Registration successful! Please login.");
        // Clear form
        document.getElementById("registerName").value = "";
        document.getElementById("registerEmail").value = "";
        document.getElementById("registerPassword").value = "";
        document.getElementById("confirmPassword").value = "";

        // Switch to login view
        setTimeout(() => {
          window.goTo("home"); // or switch to login modal
        }, 1500);
      } else {
        showToast(result.message || "Registration failed");
      }
    } catch (error) {
      console.error("Registration error:", error);
      showToast("Registration error. Please try again.");
    }
  };

  // Logout function
  window.logoutUser = function () {
    AuthAPI.logout();
    showToast("Logged out successfully");
    setTimeout(() => {
      window.location.href = "#home";
    }, 1000);
  };

  // Check login status and update UI
  window.updateAuthUI = function () {
    const user = AuthAPI.getCurrentUser();
    const isLoggedIn = AuthAPI.isUserLoggedIn();

    const userMenuEl = document.getElementById("userMenu");
    const loginBtnEl = document.getElementById("loginBtn");

    if (isLoggedIn && user) {
      if (userMenuEl) {
        userMenuEl.innerHTML = `
          <span>Welcome, ${user.name}!</span>
          <button onclick="logoutUser()" class="btn-logout">Logout</button>
        `;
      }
      if (loginBtnEl) {
        loginBtnEl.style.display = "none";
      }
    } else {
      if (userMenuEl) {
        userMenuEl.innerHTML = "";
      }
      if (loginBtnEl) {
        loginBtnEl.style.display = "block";
      }
    }
  };

  // Initialize UI on load
  updateAuthUI();
}
