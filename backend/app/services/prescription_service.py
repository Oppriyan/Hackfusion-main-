from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from app.models.database import get_db


# -------------------------------------------------
# CONFIG
# -------------------------------------------------

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------
# UPLOAD PRESCRIPTION FILE
# -------------------------------------------------

def upload_prescription(customer_id, medicine_id, file):

    if not customer_id or not medicine_id or not file:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "customer_id, medicine_id and file are required"
        }, 400

    if not allowed_file(file.filename):
        return {
            "status": "error",
            "code": "invalid_file",
            "message": "Only PDF, JPG, PNG allowed"
        }, 400

    filename = secure_filename(file.filename)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(file_path)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO prescriptions
            (customer_id, medicine_id, file_path, status, uploaded_at)
            VALUES (?, ?, ?, 'Pending', ?)
        """, (
            customer_id,
            medicine_id,
            file_path,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "Prescription uploaded successfully. Awaiting approval."
        }, 201

    except Exception:
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Upload failed"
        }, 500


# -------------------------------------------------
# ADMIN APPROVAL
# -------------------------------------------------

def approve_prescription(customer_id: str, medicine_id: int, approve: bool = True):

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id FROM prescriptions
            WHERE customer_id = ? AND medicine_id = ?
        """, (customer_id, medicine_id))

        record = cursor.fetchone()

        if not record:
            conn.close()
            return {
                "status": "error",
                "code": "not_found",
                "message": "Prescription not found"
            }, 404

        if not approve:
            cursor.execute("""
                UPDATE prescriptions
                SET status = 'Rejected'
                WHERE customer_id = ? AND medicine_id = ?
            """, (customer_id, medicine_id))

            conn.commit()
            conn.close()

            return {
                "status": "success",
                "message": "Prescription rejected"
            }, 200

        now = datetime.utcnow()
        expires_at = now + timedelta(days=30)

        cursor.execute("""
            UPDATE prescriptions
            SET status = 'Approved',
                verified_at = ?,
                expires_at = ?
            WHERE customer_id = ? AND medicine_id = ?
        """, (
            now.isoformat(),
            expires_at.isoformat(),
            customer_id,
            medicine_id
        ))

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "message": "Prescription approved",
            "valid_until": expires_at.isoformat()
        }, 200

    except Exception:
        conn.rollback()
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Approval failed"
        }, 500


# -------------------------------------------------
# CHECK IF VERIFIED (Used By Order Service)
# -------------------------------------------------

def is_verified(customer_id: str, medicine_id: int):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status, expires_at
        FROM prescriptions
        WHERE customer_id = ? AND medicine_id = ?
    """, (customer_id, medicine_id))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    if row["status"] != "Approved":
        return False

    try:
        expires_at = datetime.fromisoformat(row["expires_at"])
    except Exception:
        return False

    return datetime.utcnow() <= expires_at


# -------------------------------------------------
# GET PRESCRIPTION STATUS
# -------------------------------------------------

def get_prescription_status(customer_id: str, medicine_id: int):

    if not customer_id or not medicine_id:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Missing required fields"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT status, expires_at, uploaded_at
            FROM prescriptions
            WHERE customer_id = ? AND medicine_id = ?
        """, (customer_id, medicine_id))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {
                "status": "not_uploaded"
            }, 200

        if row["status"] == "Pending":
            return {"status": "pending"}, 200

        if row["status"] == "Rejected":
            return {"status": "rejected"}, 200

        if row["status"] == "Approved":
            expires_at = datetime.fromisoformat(row["expires_at"])

            if datetime.utcnow() > expires_at:
                return {
                    "status": "expired",
                    "expired_at": row["expires_at"]
                }, 200

            return {
                "status": "valid",
                "valid_until": row["expires_at"]
            }, 200

        return {"status": "unknown"}, 200

    except Exception:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Status lookup failed"
        }, 500