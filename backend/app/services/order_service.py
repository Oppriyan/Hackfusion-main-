from app.models.database import get_db
from app.services.prescription_service import is_verified


# -------------------------------------------------
# CREATE ORDER (ID-BASED ENTERPRISE VERSION)
# -------------------------------------------------
def create_order(customer_id: str = None, medicine_id: str = None, quantity: int = None):

    # -------------------------------------------------
    # SAFE DEFAULTS
    # -------------------------------------------------

    if not customer_id:
        customer_id = "PAT999"  # Demo fallback user

    if quantity is None:
        quantity = 1

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Quantity must be an integer"
        }, 400

    if quantity <= 0:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Quantity must be positive"
        }, 400

    if not medicine_id:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Medicine ID is required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # -------------------------------------------------
        # Fetch medicine BY ID
        # -------------------------------------------------
        cursor.execute("""
            SELECT id, name, price, stock, prescription_required
            FROM medicines
            WHERE id = ?
            LIMIT 1
        """, (medicine_id,))

        medicine_row = cursor.fetchone()

        if not medicine_row:
            conn.close()
            return {
                "status": "error",
                "code": "not_found",
                "message": "Medicine not found"
            }, 404

        # -------------------------------------------------
        # Prescription Enforcement
        # -------------------------------------------------
        if medicine_row["prescription_required"] == "Yes":
            if not is_verified(customer_id, medicine_id):
                conn.close()
                return {
                    "status": "error",
                    "code": "prescription_required",
                    "message": "A valid prescription is required for this medicine."
                }, 403

        # -------------------------------------------------
        # Stock Check
        # -------------------------------------------------
        if medicine_row["stock"] < quantity:
            conn.close()
            return {
                "status": "error",
                "code": "insufficient_stock",
                "message": "Insufficient stock available.",
                "available_stock": medicine_row["stock"]
            }, 400

        total_price = medicine_row["price"] * quantity

        # -------------------------------------------------
        # Atomic Transaction
        # -------------------------------------------------
        cursor.execute("""
            UPDATE medicines
            SET stock = stock - ?
            WHERE id = ?
        """, (quantity, medicine_id))

        cursor.execute("""
            INSERT INTO orders (
                customer_id,
                product_name,
                quantity,
                purchase_date,
                total_price,
                dosage_frequency,
                prescription_required
            ) VALUES (?, ?, ?, datetime('now'), ?, ?, ?)
        """, (
            customer_id,
            medicine_row["name"],
            quantity,
            total_price,
            "N/A",
            medicine_row["prescription_required"]
        ))

        order_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "data": {
                "order_id": order_id,
                "medicine": medicine_row["name"],
                "quantity": quantity,
                "total_price": total_price
            }
        }, 201

    except Exception:
        conn.rollback()
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Transaction failed"
        }, 500


# -------------------------------------------------
# CUSTOMER ORDER HISTORY
# -------------------------------------------------
def get_customer_history(customer_id: str):

    if not customer_id:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Customer ID is required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, product_name, quantity, purchase_date, total_price
            FROM orders
            WHERE customer_id = ?
            ORDER BY purchase_date DESC
        """, (customer_id,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {
                "status": "success",
                "data": []
            }, 200

        history = []

        for row in rows:
            history.append({
                "order_id": row["id"],  # <-- IMPORTANT ADD
                "medicine": row["product_name"],
                "quantity": row["quantity"],
                "date": row["purchase_date"],
                "total_price": row["total_price"]
            })

        return {
            "status": "success",
            "data": history
        }, 200

    except Exception:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Failed to fetch order history"
        }, 500
    # -------------------------------------------------
# GET ORDER STATUS
# -------------------------------------------------

def get_order_status(order_id: int):

    if not order_id:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Order ID required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, customer_id, product_name, quantity,
                   purchase_date, total_price
            FROM orders
            WHERE id = ?
        """, (order_id,))

        order = cursor.fetchone()
        conn.close()

        if not order:
            return {
                "status": "error",
                "code": "not_found",
                "message": "Order not found"
            }, 404

        return {
            "status": "success",
            "data": {
                "order_id": order["id"],
                "customer_id": order["customer_id"],
                "medicine": order["product_name"],
                "quantity": order["quantity"],
                "purchase_date": order["purchase_date"],
                "total_price": order["total_price"],
                "status": "Confirmed"  # For hackathon simplicity
            }
        }, 200

    except Exception:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Failed to fetch order status"
        }, 500
    # -------------------------------------------------
# CANCEL ORDER
# -------------------------------------------------
def cancel_order(order_id: int):

    if not order_id:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Order ID is required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Check if order exists
        cursor.execute("""
            SELECT id, product_name, quantity
            FROM orders
            WHERE id = ?
        """, (order_id,))

        order = cursor.fetchone()

        if not order:
            conn.close()
            return {
                "status": "error",
                "code": "not_found",
                "message": "Order not found"
            }, 404

        # Restore stock
        cursor.execute("""
            UPDATE medicines
            SET stock = stock + ?
            WHERE name = ?
        """, (order["quantity"], order["product_name"]))

        # Delete order
        cursor.execute("""
            DELETE FROM orders
            WHERE id = ?
        """, (order_id,))

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "Order cancelled successfully"
        }, 200

    except Exception:
        conn.rollback()
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Failed to cancel order"
        }, 500