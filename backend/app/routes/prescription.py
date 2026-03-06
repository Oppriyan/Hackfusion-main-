from flask import Blueprint, request, jsonify
from app.services.prescription_service import (
    get_prescription_status,
    upload_prescription,
    approve_prescription
)

prescription_bp = Blueprint("prescription", __name__)


@prescription_bp.route("/upload-prescription", methods=["POST"])
def upload_prescription_route():

    customer_id = request.form.get("customer_id")
    medicine_id = request.form.get("medicine_id")  # optional
    file = request.files.get("file")

    if not customer_id or not file:
        return jsonify({
            "status": "error",
            "message": "Customer ID and file required"
        }), 400

    response, status = upload_prescription(customer_id, medicine_id, file)
    return jsonify(response), status

@prescription_bp.route("/approve-prescription", methods=["POST"])
def approve_prescription_route():

    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Request body required"}), 400

    response, status = approve_prescription(
        data.get("customer_id"),
        data.get("medicine_id"),
        data.get("approve", True)
    )

    return jsonify(response), status


@prescription_bp.route("/prescription-status", methods=["POST"])
def prescription_status_route():

    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Request body required"}), 400

    response, status = get_prescription_status(
        data.get("customer_id"),
        data.get("medicine_id")
    )

    return jsonify(response), status