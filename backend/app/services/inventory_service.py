from app.models.database import get_db


# -------------------------------------------------
# CHECK INVENTORY (Production Search Version)
# -------------------------------------------------
def check_inventory(medicine: str):

    # -------------------------
    # Validation
    # -------------------------
    if not medicine or not isinstance(medicine, str):
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Medicine name is required"
        }, 400

    medicine = medicine.strip()

    if not medicine:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Medicine name cannot be empty"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Case-insensitive partial search
        cursor.execute("""
            SELECT id, name, price, stock, prescription_required
            FROM medicines
            WHERE LOWER(name) LIKE LOWER(?)
        """, (f"%{medicine}%",))

        rows = cursor.fetchall()

        if not rows:
            conn.close()
            return {
                "status": "error",
                "code": "not_found",
                "message": "Medicine not found"
            }, 404

        results = []

        for row in rows:
            results.append({
                "medicine_id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "stock": row["stock"],
                "available": row["stock"] > 0,
                "prescription_required": row["prescription_required"]
            })

        conn.close()

        return {
            "status": "success",
            "count": len(results),
            "data": results
        }, 200

    except Exception:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Inventory lookup failed"
        }, 500


# -------------------------------------------------
# UPDATE STOCK (ADMIN SAFE VERSION)
# -------------------------------------------------
def update_stock(medicine: str, delta: int):

    # -------------------------
    # Validation
    # -------------------------
    if not medicine or delta is None:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Missing required fields"
        }, 400

    try:
        delta = int(delta)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Delta must be integer"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Case-insensitive lookup
        cursor.execute("""
            SELECT id, name, stock
            FROM medicines
            WHERE LOWER(name) LIKE LOWER(?)
            LIMIT 1
        """, (f"%{medicine}%",))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return {
                "status": "error",
                "code": "not_found",
                "message": "Medicine not found"
            }, 404

        new_stock = row["stock"] + delta

        if new_stock < 0:
            conn.close()
            return {
                "status": "error",
                "code": "invalid_operation",
                "message": "Stock cannot be negative"
            }, 400

        cursor.execute("""
            UPDATE medicines
            SET stock = ?
            WHERE id = ?
        """, (new_stock, row["id"]))

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "data": {
                "medicine": row["name"],
                "new_stock": new_stock
            }
        }, 200

    except Exception:
        conn.rollback()
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Stock update failed"
        }, 500
    # -------------------------------------------
# GET ALL MEDICINES
# -------------------------------------------

from app.models.database import get_db

def get_all_medicines():

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, name, price, stock, prescription_required
            FROM medicines
        """)

        rows = cursor.fetchall()
        conn.close()

        medicines = []

        for row in rows:
            medicines.append({
                "id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "stock": row["stock"],
                "prescription_required": row["prescription_required"]
            })

        return {
            "status": "success",
            "data": medicines
        }, 200

    except Exception:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Failed to fetch medicines"
        }, 500
        # -------------------------------------------
# SEARCH MEDICINES
# -------------------------------------------

def search_medicines(query: str):

    if not query:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Search query required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, name, price, stock, prescription_required
            FROM medicines
            WHERE LOWER(name) LIKE ?
        """, (f"%{query.lower()}%",))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {
                "status": "success",
                "data": []
            }, 200

        results = []

        for row in rows:
            results.append({
                "id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "stock": row["stock"],
                "prescription_required": row["prescription_required"]
            })

        return {
            "status": "success",
            "data": results
        }, 200

    except Exception:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Search failed"
        }, 500