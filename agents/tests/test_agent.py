# ============================================================
# PHARMLY FINAL ROUND TEST SUITE
# ============================================================

import requests

BASE = "http://localhost:5000"

# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def safe_post(endpoint, payload):
    try:
        r = requests.post(f"{BASE}{endpoint}", json=payload)
        print("STATUS:", r.status_code)
        print("RESPONSE:", r.json())
    except Exception as e:
        print("ERROR:", e)

def safe_get(endpoint):
    try:
        r = requests.get(f"{BASE}{endpoint}")
        print("STATUS:", r.status_code)
        print("RESPONSE:", r.json())
    except Exception as e:
        print("ERROR:", e)

# ============================================================
# CHAT FLOW TESTS
# ============================================================

def test_chat(message):
    print("\nINPUT:", message)
    try:
        r = requests.post(f"{BASE}/chat", json={"message": message})
        print("OUTPUT:", r.json())
    except Exception as e:
        print("ERROR:", e)


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    print_section("1️⃣ INVENTORY FETCH")
    safe_get("/inventory/medicines")

    print_section("2️⃣ SUCCESSFUL ORDER")
    test_chat("Order 2 Paracetamol")

    print_section("3️⃣ PRESCRIPTION REQUIRED")
    test_chat("Order 1 Alprazolam")

    print_section("4️⃣ INVENTORY CHECK")
    test_chat("Check stock of Ibuprofen")

    print_section("5️⃣ INVALID / SMALLTALK")
    test_chat("Tell me a joke")

    print_section("6️⃣ CUSTOMER HISTORY")
    test_chat("Show my order history")

    print_section("7️⃣ VERIFY PRESCRIPTION (DIRECT API)")
    safe_post("/verify-prescription", {
        "customer_id": "1",
        "medicine": "Alprazolam"
    })

    print_section("8️⃣ PRESCRIPTION STATUS CHECK")
    safe_post("/prescription-status", {
        "customer_id": "1",
        "medicine": "Alprazolam"
    })

    print_section("9️⃣ CREATE ORDER DIRECT API")
    safe_post("/create-order", {
        "customer_id": 1,
        "medicine_id": 1,
        "quantity": 1
    })

    print_section("🔟 CANCEL ORDER")
    safe_post("/cancel-order", {
        "order_id": 1
    })

    print_section("✅ TESTING COMPLETE")