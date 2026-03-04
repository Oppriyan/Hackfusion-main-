from app.models.database import get_db


def create_order_atomic(customer_id, medicine_name, quantity):
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Fetch medicine
        cursor.execute("""
            SELECT id, name, price, stock
            FROM medicines
            WHERE name LIKE ?
            LIMIT 1
        """, (f"%{medicine_name}%",))

        medicine = cursor.fetchone()

        if not medicine:
            conn.close()
            return {"error": "medicine_not_found"}, 404

        if medicine["stock"] < quantity:
            conn.close()
            return {
                "error": "insufficient_stock",
                "available_stock": medicine["stock"]
            }, 400

        total_price = medicine["price"] * quantity

        # Deduct stock
        cursor.execute("""
            UPDATE medicines
            SET stock = stock - ?
            WHERE id = ?
        """, (quantity, medicine["id"]))

        # Insert order
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
            medicine["name"],
            quantity,
            total_price,
            "N/A",
            "No"
        ))

        order_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return {
            "order_id": order_id,
            "medicine": medicine["name"],
            "quantity": quantity,
            "total_price": total_price
        }, 201

    except Exception as e:
        conn.rollback()
        conn.close()
        return {"error": "transaction_failed"}, 500