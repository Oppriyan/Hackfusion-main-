from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from app.models.database import get_db


# -------------------------------------------------
# CONFIG
# -------------------------------------------------

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
PRESCRIPTION_VALIDITY_DAYS = 30


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------
# VALIDATE MEDICINE REQUIRES PRESCRIPTION
# -------------------------------------------------

def medicine_requires_prescription(medicine_id: int) -> bool:
    """Check if a medicine requires prescription"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT prescription_required FROM medicines WHERE id = ?
        """, (medicine_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        return row["prescription_required"] == "Yes"
    except Exception:
        conn.close()
        return False


# -------------------------------------------------
# UPLOAD PRESCRIPTION FILE
# -------------------------------------------------

def upload_prescription(customer_id, medicine_id, file):
    """Upload prescription file and validate requirements"""

    # Validation
    if not customer_id or not medicine_id or not file:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Customer ID, Medicine ID, and prescription file are required"
        }, 400

    if not allowed_file(file.filename):
        return {
            "status": "error",
            "code": "invalid_file",
            "message": "Only PDF, JPG, PNG files allowed"
        }, 400

    # Check if medicine exists and requires prescription
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, prescription_required FROM medicines WHERE id = ?
        """, (medicine_id,))
        
        medicine = cursor.fetchone()
        
        if not medicine:
            conn.close()
            return {
                "status": "error",
                "code": "medicine_not_found",
                "message": "Medicine not found"
            }, 404
        
        if medicine["prescription_required"] != "Yes":
            conn.close()
            return {
                "status": "error",
                "code": "prescription_not_required",
                "message": f"'{medicine['name']}' does not require a prescription"
            }, 400
        
        # Save file
        filename = secure_filename(f"{customer_id}_{medicine_id}_{datetime.utcnow().timestamp()}_{file.filename}")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(file_path)
        
        # Check if prescription already exists
        cursor.execute("""
            SELECT id, status FROM prescriptions
            WHERE customer_id = ? AND medicine_id = ?
        """, (customer_id, medicine_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE prescriptions
                SET file_path = ?, status = 'Pending', uploaded_at = ?
                WHERE customer_id = ? AND medicine_id = ?
            """, (
                file_path,
                datetime.utcnow().isoformat(),
                customer_id,
                medicine_id
            ))
            message = "Prescription updated. Pending admin review."
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO prescriptions
                (customer_id, medicine_id, file_path, status, uploaded_at)
                VALUES (?, ?, ?, 'Pending', ?)
            """, (
                customer_id,
                medicine_id,
                file_path,
                datetime.utcnow().isoformat()
            ))
            message = "Prescription uploaded successfully. Awaiting admin approval."
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": message,
            "data": {
                "medicine_id": medicine_id,
                "medicine_name": medicine["name"],
                "prescription_status": "pending_review"
            }
        }, 201

    except Exception as e:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Prescription upload failed"
        }, 500


# -------------------------------------------------
# ADMIN APPROVAL
# -------------------------------------------------

def approve_prescription(customer_id: str, medicine_id: int, approve: bool = True):
    """Admin approves or rejects prescription"""

    if not customer_id or not medicine_id:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Customer ID and Medicine ID are required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, status, file_path FROM prescriptions
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

        # Fetch medicine info
        cursor.execute("""
            SELECT name FROM medicines WHERE id = ?
        """, (medicine_id,))
        
        medicine = cursor.fetchone()
        medicine_name = medicine["name"] if medicine else "Unknown Medicine"

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
                "message": f"Prescription for {medicine_name} rejected",
                "data": {
                    "prescription_status": "rejected",
                    "medicine_name": medicine_name
                }
            }, 200

        # Approve prescription
        now = datetime.utcnow()
        expires_at = now + timedelta(days=PRESCRIPTION_VALIDITY_DAYS)

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
            "message": f"Prescription for {medicine_name} approved",
            "data": {
                "prescription_status": "approved",
                "medicine_name": medicine_name,
                "valid_until": expires_at.isoformat(),
                "validity_days": PRESCRIPTION_VALIDITY_DAYS
            }
        }, 200

    except Exception as e:
        conn.rollback()
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Approval operation failed"
        }, 500


# -------------------------------------------------
# CHECK IF VERIFIED (Used By Order Service)
# -------------------------------------------------

def is_verified(customer_id: str, medicine_id: int) -> bool:
    """Check if prescription is valid and approved"""

    conn = get_db()
    cursor = conn.cursor()

    try:
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

        # Check if prescription is not expired
        is_valid = datetime.utcnow() <= expires_at
        return is_valid

    except Exception:
        conn.close()
        return False


# -------------------------------------------------
# GET VERIFICATION DETAILS
# -------------------------------------------------

def get_verification_details(customer_id: str, medicine_id: int):
    """Get detailed verification status for frontend display"""

    if not customer_id or not medicine_id:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Customer ID and Medicine ID required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.status, p.expires_at, p.uploaded_at, m.name
            FROM prescriptions p
            JOIN medicines m ON p.medicine_id = m.id
            WHERE p.customer_id = ? AND p.medicine_id = ?
        """, (customer_id, medicine_id))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {
                "status": "not_found",
                "data": {
                    "prescription_status": "not_uploaded",
                    "medicine_id": medicine_id
                }
            }, 200

        status = row["status"].lower()
        
        response = {
            "status": "success",
            "data": {
                "prescription_status": status,
                "medicine_id": medicine_id,
                "medicine_name": row["name"],
                "uploaded_at": row["uploaded_at"]
            }
        }

        if status == "approved":
            expires_at = datetime.fromisoformat(row["expires_at"])
            is_expired = datetime.utcnow() > expires_at
            
            response["data"]["valid_until"] = row["expires_at"]
            response["data"]["is_expired"] = is_expired
            response["data"]["days_remaining"] = max(0, (expires_at - datetime.utcnow()).days)

        return response, 200

    except Exception as e:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Status lookup failed"
        }, 500


# -------------------------------------------------
# GET PRESCRIPTION STATUS (Backend for Controller)
# -------------------------------------------------

def get_prescription_status(customer_id: str, medicine_id: int):
    """Get prescription status - returns structured response"""

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
            SELECT p.status, p.expires_at, p.uploaded_at, p.verified_at, m.name
            FROM prescriptions p
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE p.customer_id = ? AND p.medicine_id = ?
        """, (customer_id, medicine_id))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {
                "prescription_status": "not_uploaded",
                "message": "No prescription found"
            }, 200

        status = row["status"].lower()
        
        response = {
            "prescription_status": status,
            "medicine_id": medicine_id,
            "medicine_name": row["name"] or "Unknown",
            "uploaded_at": row["uploaded_at"]
        }

        if status == "pending":
            response["message"] = "Prescription uploaded, awaiting admin review"
            return response, 200

        if status == "rejected":
            response["message"] = "Prescription was rejected"
            return response, 200

        if status == "approved":
            expires_at = datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
            verified_at = datetime.fromisoformat(row["verified_at"]) if row["verified_at"] else None
            
            if expires_at and datetime.utcnow() > expires_at:
                response["prescription_status"] = "expired"
                response["expired_at"] = row["expires_at"]
                response["message"] = "Prescription has expired"
                return response, 200
            
            response["verified_at"] = row["verified_at"]
            response["valid_until"] = row["expires_at"]
            response["days_remaining"] = (expires_at - datetime.utcnow()).days if expires_at else 0
            response["message"] = "Prescription is valid"
            return response, 200

        return {
            "prescription_status": "unknown",
            "message": "Unknown prescription status"
        }, 200

    except Exception as e:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Status lookup failed"
        }, 500


# -------------------------------------------------
# GET PENDING PRESCRIPTIONS (ADMIN)
# -------------------------------------------------

def get_pending_prescriptions():
    """Get all pending prescriptions for admin review"""

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.id, p.customer_id, p.medicine_id, p.uploaded_at, m.name
            FROM prescriptions p
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE p.status = 'Pending'
            ORDER BY p.uploaded_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        pending_list = [{
            "id": row["id"],
            "customer_id": row["customer_id"],
            "medicine_id": row["medicine_id"],
            "medicine_name": row["name"] or "Unknown",
            "uploaded_at": row["uploaded_at"]
        } for row in rows]

        return {
            "status": "success",
            "data": pending_list,
            "count": len(pending_list)
        }, 200

    except Exception:
        conn.close()
        return {
            "status": "error",
            "code": "internal_error",
            "message": "Failed to fetch pending prescriptions"
        }, 500