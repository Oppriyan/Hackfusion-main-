from flask import Blueprint, request, jsonify
from app.services.prescription_service import (
    get_prescription_status,
    upload_prescription,
    approve_prescription,
    get_pending_prescriptions,
    medicine_requires_prescription
)

prescription_bp = Blueprint("prescription", __name__)


@prescription_bp.route("/upload-prescription", methods=["POST"])
def upload_prescription_route():
    """Upload prescription file for a medicine"""

    customer_id = request.form.get("customer_id")
    medicine_id = request.form.get("medicine_id")
    file = request.files.get("file")

    if not customer_id or not medicine_id or not file:
        return jsonify({
            "status": "error",
            "message": "Customer ID, Medicine ID, and prescription file are required"
        }), 400

    response, status = upload_prescription(customer_id, medicine_id, file)
    return jsonify(response), status


@prescription_bp.route("/approve-prescription", methods=["POST"])
def approve_prescription_route():
    """Admin approves or rejects prescription"""

    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Request body required"}), 400

    customer_id = data.get("customer_id")
    medicine_id = data.get("medicine_id")
    approve = data.get("approve", True)

    if not customer_id or not medicine_id:
        return jsonify({
            "status": "error",
            "message": "Customer ID and Medicine ID are required"
        }), 400

    response, status = approve_prescription(customer_id, medicine_id, approve)
    return jsonify(response), status


@prescription_bp.route("/check-prescription", methods=["POST"])
def check_prescription_route():
    """Check prescription status"""

    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Request body required"}), 400

    customer_id = data.get("customer_id")
    medicine_id = data.get("medicine_id")

    if not customer_id or not medicine_id:
        return jsonify({
            "status": "error",
            "message": "Customer ID and Medicine ID are required"
        }), 400

    response, status = get_prescription_status(customer_id, medicine_id)
    return jsonify(response), status


@prescription_bp.route("/pending-prescriptions", methods=["GET"])
def pending_prescriptions_route():
    """Get all pending prescriptions (Admin)"""

    response, status = get_pending_prescriptions()
    return jsonify(response), status


@prescription_bp.route("/medicine-requires-prescription/<int:medicine_id>", methods=["GET"])
def check_medicine_prescription_route(medicine_id):
    """Check if a medicine requires prescription"""

    requires = medicine_requires_prescription(medicine_id)
    
    return jsonify({
        "status": "success",
        "medicine_id": medicine_id,
        "requires_prescription": requires
    }), 200