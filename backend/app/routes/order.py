from flask import Blueprint, request, jsonify
from app.services.order_service import (
    create_order,
    get_customer_history,
    cancel_order,
    get_order_status
)

order_bp = Blueprint("order", __name__)


@order_bp.route("/create-order", methods=["POST"])
def create_order_route():

    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Request body required"}), 400

    customer_id = data.get("customer_id")
    medicine_id = data.get("medicine_id")
    quantity = data.get("quantity")

    if not customer_id or not medicine_id or not quantity:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except:
        return jsonify({"status": "error", "message": "Invalid quantity"}), 400

    response, status = create_order(customer_id, medicine_id, quantity)
    return jsonify(response), status


@order_bp.route("/customer-history/<customer_id>", methods=["GET"])
def customer_history_route(customer_id):

    response, status = get_customer_history(customer_id)
    return jsonify(response), status


@order_bp.route("/cancel-order", methods=["POST"])
def cancel_order_route():

    data = request.get_json()

    if not data or not data.get("order_id"):
        return jsonify({"status": "error", "message": "order_id required"}), 400

    response, status = cancel_order(data["order_id"])
    return jsonify(response), status


@order_bp.route("/order-status/<int:order_id>", methods=["GET"])
def order_status_route(order_id):

    response, status = get_order_status(order_id)
    return jsonify(response), status