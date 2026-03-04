from flask import Blueprint, jsonify, request
from app.services.inventory_service import (
    check_inventory,
    update_stock,
    get_all_medicines,
    search_medicines
)
from app.utils.auth_utils import require_role

inventory_bp = Blueprint("inventory", __name__)


# -------------------------------------------------
# GET ALL MEDICINES
# -------------------------------------------------
@inventory_bp.route("/medicines", methods=["GET"])
def get_medicines_route():
    try:
        response, status = get_all_medicines()
        return jsonify(response), status
    except Exception:
        return jsonify({
            "status": "error",
            "code": "internal_error",
            "message": "Failed to fetch medicines"
        }), 500


# -------------------------------------------------
# SEARCH MEDICINES
# -------------------------------------------------
@inventory_bp.route("/search", methods=["GET"])
def search_route():
    try:
        query = request.args.get("query")

        if not query:
            return jsonify({
                "status": "error",
                "code": "validation_error",
                "message": "Search query required"
            }), 400

        response, status = search_medicines(query)
        return jsonify(response), status

    except Exception:
        return jsonify({
            "status": "error",
            "code": "internal_error",
            "message": "Search endpoint failed"
        }), 500


# -------------------------------------------------
# GET SINGLE MEDICINE INVENTORY
# -------------------------------------------------
@inventory_bp.route("/<medicine>", methods=["GET"])
def inventory(medicine):
    try:
        response, status_code = check_inventory(medicine)
        return jsonify(response), status_code
    except Exception:
        return jsonify({
            "status": "error",
            "code": "internal_error",
            "message": "Inventory endpoint failed"
        }), 500


# -------------------------------------------------
# UPDATE STOCK (ADMIN PROTECTED - JWT BASED)
# -------------------------------------------------
@inventory_bp.route("/update-stock", methods=["POST"])
@require_role("admin")
def update_stock_route():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "code": "validation_error",
                "message": "Request body required"
            }), 400

        medicine = data.get("medicine")
        delta = data.get("delta")

        response, status = update_stock(medicine, delta)
        return jsonify(response), status

    except Exception:
        return jsonify({
            "status": "error",
            "code": "internal_error",
            "message": "Stock update endpoint failed"
        }), 500