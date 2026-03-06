import { OrderAPI, CheckoutAPI, PrescriptionAPI, AuthAPI, InventoryAPI } from "../api.js";
import { cartItems } from "../state.js";

export function initPayment() {
  window.processPayment = async function () {
    console.log("Processing payment...");

    if (cartItems.length === 0) {
      showToast("Your cart is empty");
      return;
    }

    // Get current user
    const user = AuthAPI.getCurrentUser();
    const customerId = user?.id || "PAT999";

    // Show loading state
    const paymentBtn = document.getElementById("paymentBtn");
    if (paymentBtn) {
      paymentBtn.disabled = true;
      paymentBtn.textContent = "Processing...";
    }

    try {
      // Check for prescriptions if needed
      for (const item of cartItems) {
        // Check if medicine requires prescription
        const prescReq = await InventoryAPI.checkMedicineRequiresPrescription(
          item.id
        );

        if (prescReq.requires_prescription) {
          // Check if prescription is valid
          const prescStatus = await PrescriptionAPI.checkPrescriptionStatus(
            customerId,
            item.id
          );

          if (
            prescStatus.prescription_status !== "approved" ||
            prescStatus.is_expired
          ) {
            showToast(
              `Prescription required for ${item.name}. Please upload first.`
            );
            if (paymentBtn) {
              paymentBtn.disabled = false;
              paymentBtn.textContent = "Process Payment";
            }
            return;
          }
        }
      }

      // Process each order
      for (const item of cartItems) {
        const orderResponse = await OrderAPI.createOrder(
          customerId,
          item.id,
          item.qty
        );

        if (orderResponse.status !== "success") {
          showToast(`Failed to create order for ${item.name}`);
          if (paymentBtn) {
            paymentBtn.disabled = false;
            paymentBtn.textContent = "Process Payment";
          }
          return;
        }
      }

      // Success
      cartItems.length = 0; // Clear cart
      renderCart();
      showToast("Payment successful! Orders created.");

      // Redirect to dashboard or order history
      setTimeout(() => {
        window.location.href = "#dashboard";
      }, 1500);
    } catch (error) {
      console.error("Payment error:", error);
      showToast("Payment processing failed");
    } finally {
      if (paymentBtn) {
        paymentBtn.disabled = false;
        paymentBtn.textContent = "Process Payment";
      }
    }
  };

  // Upload prescription function
  window.uploadPrescription = async function (medicineId) {
    const fileInput = document.getElementById(`prescFile-${medicineId}`);

    if (!fileInput || !fileInput.files[0]) {
      showToast("Please select a file");
      return;
    }

    const user = AuthAPI.getCurrentUser();
    const customerId = user?.id || "PAT999";
    const file = fileInput.files[0];

    try {
      const response = await PrescriptionAPI.uploadPrescription(
        customerId,
        medicineId,
        file
      );

      if (response.status === "success") {
        showToast(response.message || "Prescription uploaded successfully");
        fileInput.value = ""; // Clear file input
      } else {
        showToast(response.message || "Upload failed");
      }
    } catch (error) {
      console.error("Prescription upload error:", error);
      showToast("Failed to upload prescription");
    }
  };

  // Check prescription status
  window.checkPrescriptionStatus = async function (medicineId) {
    const user = AuthAPI.getCurrentUser();
    const customerId = user?.id || "PAT999";

    try {
      const status = await PrescriptionAPI.checkPrescriptionStatus(
        customerId,
        medicineId
      );

      let message = "";
      switch (status.prescription_status) {
        case "not_uploaded":
          message = "No prescription uploaded yet";
          break;
        case "pending":
          message = "Prescription pending admin review";
          break;
        case "approved":
          message = `Prescription valid until ${status.valid_until}`;
          break;
        case "rejected":
          message = "Prescription was rejected - please upload a new one";
          break;
        case "expired":
          message = "Prescription expired - please upload a new one";
          break;
        default:
          message = status.message || "Unknown status";
      }

      showToast(message);
      return status;
    } catch (error) {
      console.error("Status check error:", error);
      showToast("Failed to check prescription status");
    }
  };

  // Set payment tab
  window.setPayTab = function(element, tabName) {
    // Remove active class from all tabs
    document.querySelectorAll(".pay-tab").forEach(tab => {
      tab.classList.remove("active");
      tab.setAttribute("aria-pressed", "false");
    });

    // Add active class to clicked tab
    if (element) {
      element.classList.add("active");
      element.setAttribute("aria-pressed", "true");
    }

    // Hide all payment methods
    document.querySelectorAll(".pay-method").forEach(method => {
      method.style.display = "none";
    });

    // Show selected payment method
    const payMethod = document.getElementById("pay-" + tabName);
    if (payMethod) {
      payMethod.style.display = "block";
    }
  };

  // Reset payment modal
  window.resetPayModal = function() {
    document.querySelectorAll(".pay-tab").forEach(tab => {
      tab.classList.remove("active");
      tab.setAttribute("aria-pressed", "false");
    });

    const firstTab = document.querySelector(".pay-tab");
    if (firstTab) {
      firstTab.classList.add("active");
      firstTab.setAttribute("aria-pressed", "true");
    }

    document.querySelectorAll(".pay-method").forEach(method => {
      method.style.display = "none";
    });

    const firstMethod = document.querySelector(".pay-method");
    if (firstMethod) {
      firstMethod.style.display = "block";
    }
  };
}
