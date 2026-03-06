import os
import requests
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

BASE_URL = os.getenv("AGENT_BASE_URL", "http://localhost:5000")


def safe_request(method, endpoint, **kwargs):

    try:

        url = f"{BASE_URL}{endpoint}"

        response = requests.request(
            method,
            url,
            timeout=5,
            **kwargs
        )

        if not response.text:
            return {"status": "error", "reason": "Empty response"}

        return response.json()

    except requests.exceptions.Timeout:

        return {
            "status": "error",
            "reason": "Service timeout"
        }

    except Exception as e:

        return {
            "status": "error",
            "reason": str(e)
        }


# HEALTH

def health_check():
    return safe_request("GET", "/health")


# INVENTORY

@traceable(name="Check-Inventory")
def check_inventory(medicine_name):
    return safe_request("GET", f"/inventory/{medicine_name}")


def get_all_medicines():
    return safe_request("GET", "/inventory/medicines")


def search_medicines(query):
    return safe_request("GET", f"/inventory/search?query={query}")


def update_stock(medicine, delta, admin_token):

    return safe_request(
        "POST",
        "/inventory/update-stock",
        headers={"X-ADMIN-TOKEN": admin_token},
        json={
            "medicine": medicine,
            "delta": delta
        }
    )


# ORDERS

@traceable(name="Create-Order")
def create_order(customer_id, medicine_id, quantity):

    return safe_request(
        "POST",
        "/create-order",
        json={
            "customer_id": customer_id,
            "medicine_id": medicine_id,
            "quantity": quantity
        }
    )


@traceable(name="Get-History")
def get_customer_history(customer_id):

    return safe_request(
        "GET",
        f"/customer-history/{customer_id}"
    )


def cancel_order(order_id):

    return safe_request(
        "POST",
        "/cancel-order",
        json={"order_id": order_id}
    )


def get_order_status(order_id):

    return safe_request(
        "GET",
        f"/order-status/{order_id}"
    )


# PRESCRIPTION

@traceable(name="Verify-Prescription")
def verify_prescription(customer_id, medicine_identifier):

    return safe_request(
        "POST",
        "/verify-prescription",
        json={
            "customer_id": str(customer_id),
            "medicine": str(medicine_identifier)
        }
    )


@traceable(name="Prescription-Status")
def check_prescription_status(customer_id, medicine_name):

    return safe_request(
        "POST",
        "/prescription-status",
        json={
            "customer_id": str(customer_id),
            "medicine": str(medicine_name)
        }
    )


def upload_prescription_file(customer_id, medicine_id, file_path):

    with open(file_path, "rb") as f:

        return safe_request(
            "POST",
            "/upload-prescription",
            files={"file": f},
            data={
                "customer_id": customer_id,
                "medicine_id": medicine_id
            }
        )