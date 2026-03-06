import { PrescriptionAPI, AuthAPI } from "../api.js";

export function initAdmin() {
  // Check if user is admin
  window.loadAdminPanel = async function () {
    const user = AuthAPI.getCurrentUser();

    if (!user || user.role !== "admin") {
      showToast("Admin access required");
      return;
    }

    try {
      await loadPendingPrescriptions();
    } catch (error) {
      console.error("Admin panel error:", error);
    }
  };

  // Load pending prescriptions
  async function loadPendingPrescriptions() {
    try {
      const pendingEl = document.getElementById("pendingPrescriptions");
      if (!pendingEl) return;

      pendingEl.innerHTML = "<div class='loading'>Loading pending prescriptions...</div>";

      const response = await PrescriptionAPI.getPendingPrescriptions();

      if (response.status === "success" && response.data) {
        const prescriptions = response.data;

        if (prescriptions.length === 0) {
          pendingEl.innerHTML =
            "<p class='empty'>No pending prescriptions</p>";
          return;
        }

        pendingEl.innerHTML = `
          <table class="prescriptions-table">
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Medicine</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${prescriptions
                .map(
                  (p) => `
                <tr>
                  <td>${p.customer_id}</td>
                  <td>${p.medicine_name}</td>
                  <td>${new Date(p.uploaded_at).toLocaleDateString()}</td>
                  <td>
                    <button 
                      onclick="approvePrescriptionAdmin('${p.customer_id}', ${p.medicine_id})"
                      class="btn btn-success">
                      Approve
                    </button>
                    <button 
                      onclick="rejectPrescriptionAdmin('${p.customer_id}', ${p.medicine_id})"
                      class="btn btn-danger">
                      Reject
                    </button>
                  </td>
                </tr>
              `
                )
                .join("")}
            </tbody>
          </table>
        `;
      } else {
        pendingEl.innerHTML =
          "<p>Failed to load prescriptions</p>";
      }
    } catch (error) {
      console.error("Prescription loading error:", error);
      const pendingEl = document.getElementById("pendingPrescriptions");
      if (pendingEl) {
        pendingEl.innerHTML = "<p>Error loading prescriptions</p>";
      }
    }
  }

  // Approve prescription
  window.approvePrescriptionAdmin = async function (customerId, medicineId) {
    if (!confirm("Approve this prescription?")) return;

    try {
      const response = await PrescriptionAPI.approvePrescription(
        customerId,
        medicineId,
        true
      );

      if (response.status === "success") {
        showToast(response.message || "Prescription approved");
        await loadPendingPrescriptions();
      } else {
        showToast(response.message || "Approval failed");
      }
    } catch (error) {
      console.error("Approval error:", error);
      showToast("Error approving prescription");
    }
  };

  // Reject prescription
  window.rejectPrescriptionAdmin = async function (customerId, medicineId) {
    if (!confirm("Reject this prescription?")) return;

    try {
      const response = await PrescriptionAPI.rejectPrescription(
        customerId,
        medicineId
      );

      if (response.status === "success") {
        showToast(response.message || "Prescription rejected");
        await loadPendingPrescriptions();
      } else {
        showToast(response.message || "Rejection failed");
      }
    } catch (error) {
      console.error("Rejection error:", error);
      showToast("Error rejecting prescription");
    }
  };

  // Show admin section
  window.showAdminSec = function(section, element) {
    // Hide all sections
    document.querySelectorAll(".admin-sec").forEach(sec => {
      sec.classList.remove("active");
    });

    // Show selected section
    const selectedSec = document.getElementById("asec-" + section);
    if (selectedSec) {
      selectedSec.classList.add("active");
    }

    // Update button states
    if (element) {
      document.querySelectorAll(".sb-btn").forEach(btn => {
        btn.classList.remove("active");
        btn.setAttribute("aria-pressed", "false");
      });
      element.classList.add("active");
      element.setAttribute("aria-pressed", "true");
    }
  };

  // Load admin panel on init
  console.log("Admin panel initialized");
}
