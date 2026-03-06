# agents/core/controller.py

from langsmith import traceable
from datetime import datetime
from agents.tools.webhook import trigger_admin_alert
from agents.utils.safe_execute import safe_execute

from agents.tools.tools import (
    check_inventory,
    create_order,
    verify_prescription,
    check_prescription_status,
    get_customer_history,
    cancel_order,
    get_order_status,
    search_medicines
)

DEFAULT_CUSTOMER = "PAT001"


@traceable(name="Controller-Decision")
def handle_intent(request, user_input=None):

    try:

        if not request:
            return {"status": "error", "message": "Invalid request"}

        intent = request.intent
        customer_id = request.customer_id or DEFAULT_CUSTOMER
        medicine = request.medicine_name
        quantity = request.quantity

        user_input_lower = (user_input or "").lower()

        # --------------------------------------------------
        # HARD COMMANDS
        # --------------------------------------------------

        if "cancel order" in user_input_lower:
            try:
                order_id = int(user_input_lower.split("cancel order")[1].strip())
                return safe_execute(cancel_order, order_id)
            except Exception:
                return {"status": "error", "message": "Invalid order ID"}

        if "order status" in user_input_lower:
            try:
                order_id = int(user_input_lower.split("order status")[1].strip())
                return safe_execute(get_order_status, order_id)
            except Exception:
                return {"status": "error", "message": "Invalid order ID"}

        if "search" in user_input_lower:
            query = user_input_lower.replace("search", "").strip()

            if not query:
                return {"status": "error", "message": "Invalid search query"}

            return safe_execute(search_medicines, query)

        # --------------------------------------------------
        # INVENTORY
        # --------------------------------------------------

        if intent == "inventory":

            if not medicine:
                return {"status": "error", "code": "missing_medicine"}

            return safe_execute(check_inventory, medicine)

        # --------------------------------------------------
        # ORDER
        # --------------------------------------------------

        if intent == "order":

            if not medicine:
                return {"status": "error", "code": "missing_medicine"}

            if quantity is None or quantity <= 0:
                return {
                    "status": "error",
                    "code": "invalid_quantity",
                    "message": "Quantity must be greater than 0"
                }

            inventory = safe_execute(check_inventory, medicine)

            if inventory.get("status") != "success":
                return inventory

            data_list = inventory.get("data", [])

            if not data_list:
                return {"status": "error", "code": "not_found"}

            item = data_list[0]

            medicine_id = item.get("medicine_id")
            prescription_required = item.get("prescription_required") == "Yes"

            # Prescription check
            if prescription_required:

                status_check = safe_execute(
                    check_prescription_status,
                    customer_id,
                    item.get("name")
                )

                if status_check.get("status") != "valid":
                    return {
                        "status": "error",
                        "code": "prescription_required"
                    }

            # Create order
            result = safe_execute(
                create_order,
                customer_id,
                medicine_id,
                quantity
            )

            # webhook safe
            if result.get("status") == "success":

                order_data = result.get("data", {})

                try:

                    trigger_admin_alert(
                        event_type="order_created",
                        payload={
                            "order_id": order_data.get("order_id"),
                            "customer_id": customer_id,
                            "medicine": order_data.get("medicine"),
                            "quantity": order_data.get("quantity"),
                            "total_price": order_data.get("total_price"),
                            "date": datetime.utcnow().isoformat()
                        }
                    )

                except Exception as e:
                    print("Webhook error:", str(e))

            return result

        # --------------------------------------------------
        # PRESCRIPTION VERIFY
        # --------------------------------------------------

        if intent == "upload_prescription":

            if not medicine:
                return {"status": "error", "code": "missing_medicine"}

            inventory = safe_execute(check_inventory, medicine)

            if inventory.get("status") != "success":
                return inventory

            data_list = inventory.get("data", [])

            if not data_list:
                return {"status": "error", "code": "not_found"}

            item = data_list[0]

            medicine_name = item.get("name")

            return safe_execute(
                verify_prescription,
                customer_id,
                medicine_name
            )

        # --------------------------------------------------
        # HISTORY
        # --------------------------------------------------

        if intent == "history":
            return safe_execute(get_customer_history, customer_id)

        return {"status": "smalltalk"}

    except Exception as e:

        print("Controller Error:", str(e))

        return {
            "status": "error",
            "message": "Internal controller error"
        }