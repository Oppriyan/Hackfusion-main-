from app.models.database import get_db


def get_medicine_by_name(name: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, price, stock
        FROM medicines
        WHERE name LIKE ?
        LIMIT 1
    """, (f"%{name}%",))

    row = cursor.fetchone()
    conn.close()

    return row