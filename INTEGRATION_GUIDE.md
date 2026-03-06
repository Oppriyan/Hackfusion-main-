# Pharmly Complete Integration Guide

## Overview

Pharmly is a 4-layer AI pharmacy system with complete backend, frontend, and voice integration:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (User Interface)                │
│  ┌─────────────┬─────────────┬──────────────┬─────────────┐ │
│  │   Shop      │   Cart      │   Dashboard  │   Admin     │ │
│  │   Chatbot   │   Voice     │   Payment    │   Auth      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              ↓                                 │
│                     API Client (api.js)                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
         ┌────────────────────────────────────────────┐
         │     BACKEND (Flask + Agent System)         │
         │  ┌──────────────────────────────────────┐  │
         │  │   Routes (Chat, Order, Inventory)   │  │
         │  │        ↓                             │  │
         │  │   Agent Pipeline                    │  │
         │  │  ┌────────────────────────────────┐ │  │
         │  │  │  1. Extractor (Intent)        │ │  │
         │  │  │  2. Controller (Logic)        │ │  │
         │  │  │  3. Responder (Response)      │ │  │
         │  │  │  4. Tools (Pharmacy Tasks)    │ │  │
         │  │  └────────────────────────────────┘ │  │
         │  │        ↓                             │  │
         │  │   Database (SQLite)                 │  │
         │  └──────────────────────────────────────┘  │
         └────────────────────────────────────────────┘
                              ↓
         ┌────────────────────────────────────────────┐
         │         External Services                  │
         │  • Azure OpenAI (NLP)                      │
         │  • VAPI (Voice AI)                         │
         │  • Webhooks (Automation)                   │
         └────────────────────────────────────────────┘
```

---

## System Components

### 1. Frontend (HTML/CSS/JavaScript)

**Structure:**
```
Frontend/
  └── js/
      ├── api.js              # API client (all endpoints)
      ├── app.js              # Main initialization
      ├── state.js            # Shared state
      └── modules/
          ├── auth.js         # Login/Register
          ├── shop.js         # Medicine search & display
          ├── cart.js         # Shopping cart
          ├── payment.js      # Checkout & Rx validation
          ├── chatbot.js      # Text chat interface
          ├── voice.js        # Voice call handler (VAPI)
          ├── dashboard.js    # User analytics
          ├── admin.js        # Prescription approval
          └── ...other modules
```

**Key Features:**
- Real-time API calls
- Form validation
- State management
- Toast notifications
- Loading indicators

### 2. Backend (Python/Flask)

**Structure:**
```
backend/
  └── app/
      ├── routes/
      │   ├── auth.py         # User authentication
      │   ├── chat.py         # Chat & voice endpoints
      │   ├── inventory.py    # Medicine search
      │   ├── order.py        # Order management
      │   └── prescription.py # Rx upload & approval
      ├── services/
      │   ├── agent_service.py    # Agent orchestration
      │   ├── order_service.py    # Order logic
      │   ├── prescription_service.py  # Rx validation
      │   └── inventory_service.py     # Stock checks
      ├── models/
      │   └── database.py     # SQLite schema
      └── utils/
          ├── auth_utils.py
          └── ...other utilities
```

**Key Features:**
- RESTful API endpoints
- Database abstraction
- Error handling
- CORS support

### 3. Agent System (Autonomous AI)

**Structure:**
```
agents/
  └── core/
      ├── agent_runner.py    # Main orchestrator
      ├── extractor.py       # Intent recognition (Azure OpenAI)
      ├── controller.py      # Business logic
      ├── responder.py       # Response generation
      └── predictor.py       # ML predictions
  ├── tools/
  │   ├── tools.py          # Service calls (inventory, orders, etc)
  │   └── webhook.py        # External webhooks
  ├── models/
  │   └── schemas.py        # Data models (Pydantic)
  └── utils/
      └── safe_execute.py   # Safe execution wrapper
```

**Agent Pipeline:**

```
User Input
  ↓
[Extractor] Intent Recognition (GPT-4o)
  - Identifies intent (order, inventory, upload_prescription, etc)
  - Extracts entities (medicine_name, quantity, customer_id)
  - Returns StructuredRequest
  ↓
[Controller] Business Logic
  - Validates request
  - Calls appropriate tools (check_inventory, create_order, etc)
  - Handles prescription verification
  - Returns result dict
  ↓
[Responder] Response Generation
  - Formats result as natural language
  - Creates friendly message
  - Handles errors gracefully
  ↓
Final Response to User (Text or Voice)
```

---

## Integration Points

### Frontend → Backend

**API Client (api.js):**
```javascript
// All API calls go through centralized client
const response = await OrderAPI.createOrder(customerId, medicineId, quantity);
const medicines = await InventoryAPI.getAllMedicines();
const status = await PrescriptionAPI.checkPrescriptionStatus(customerId, medicineId);
```

**Error Handling:**
- All 4xx/5xx errors caught and displayed as toasts
- User-friendly error messages
- Automatic retry logic (optional)

### Backend → Agent System

**Integration Point (agent_service.py):**
```python
def process_chat_message(message, customer_id):
    # This calls the agent pipeline
    agent_result = run_agent(message)
    return format_response(agent_result)
```

**Chat Endpoint:**
```
POST /chat/message
{
  "message": "Order 2 paracetamol",
  "customer_id": "PAT001"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "reply": "Order #15 created: 2x Paracetamol €4.12"
  }
}
```

### Agent System → Backend Services

**Tools (agents/tools/tools.py):**
```python
# Agent calls backend internally
check_inventory("paracetamol")
create_order("PAT001", 1, 2)
verify_prescription("PAT001", 1)

# These make HTTP calls to:
# GET /inventory/paracetamol
# POST /create-order
# POST /prescription/check-prescription
```

### Backend → Database

**SQLite Integration:**
```python
# All queries go through database.py
conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))
```

**Tables:**
- `medicines` - Product catalog
- `customers` - User profiles
- `orders` - Order history
- `prescriptions` - Rx management
- `users` - Admin accounts

### Voice Integration (VAPI)

**Flow:**
```
User Calls Phone Number
  ↓
VAPI Transcribes Speech
  ↓
VAPI sends to /chat/voice-webhook
  ↓
Backend processes through agent
  ↓
Response sent back to VAPI
  ↓
VAPI Converts to Speech
  ↓
User Hears Response
```

**Configuration (.env):**
```env
VAPI_AGENT_ID=your_agent_id
VAPI_PUBLIC_KEY=your_public_key
VAPI_API_KEY=your_api_key
AGENT_BASE_URL=http://localhost:5000
```

---

## Data Flow Examples

### Example 1: Order with Chatbot

```javascript
// Frontend
User: "Order 2 paracetamol"
  ↓
sendMessage("Order 2 paracetamol")
  ↓
POST /chat/message {message: "Order 2 paracetamol", customer_id: "PAT001"}
```

```python
# Backend
process_chat_message("Order 2 paracetamol", "PAT001")
  ↓
run_agent("Order 2 paracetamol")
  ↓
[Extractor] → {intent: "order", medicine_name: "paracetamol", quantity: 2}
  ↓
[Controller] → check_inventory("paracetamol") 
            → check_prescription_status("PAT001", paracetamol_id)
            → create_order("PAT001", paracetamol_id, 2)
  ↓
[Responder] → "Order #15 created: 2x Paracetamol €4.12"
```

```javascript
// Frontend Response Display
{
  status: "success",
  data: {
    reply: "Order #15 created: 2x Paracetamol €4.12"
  }
}
  ↓
Display in chat: "Order #15 created: 2x Paracetamol €4.12"
```

---

### Example 2: Voice Call with Prescription Check

```
User Calls: +49-VAPI-NUMBER
  ↓
VAPI: "Welcome to Pharmly. How can I help?"
User: "Can I order amoxicillin?"
  ↓
VAPI Transcribes: "Can I order amoxicillin?"
  ↓
POST /chat/voice-webhook
{
  "message": "Can I order amoxicillin?",
  "customer_id": "VOICE_USER",
  "call_id": "call_xyz"
}
```

```python
# Backend processing
process_voice_message("Can I order amoxicillin?", "VOICE_USER")
  ↓
run_agent("Can I order amoxicillin?")
  ↓
[Extractor] → {intent: "order", medicine_name: "amoxicillin"}
  ↓
[Controller] 
  → check_inventory("amoxicillin") → Found, stock: 2
  → check_prescription_status("VOICE_USER", amoxicillin_id) → Not verified
  → Return error: "This medicine requires a valid prescription"
  ↓
[Responder] → "Amoxicillin requires a prescription. 
              Please upload it through the app first."
```

```
Response to VAPI:
{
  "status": "success",
  "message": "Amoxicillin requires a prescription. Please upload it through the app first.",
  "call_id": "call_xyz"
}
  ↓
VAPI converts to speech and plays: "Amoxicillin requires a prescription..."
```

---

## Authentication

### Frontend
```javascript
// Login
const result = await AuthAPI.login(email, password);
localStorage.setItem("auth_token", result.token);
localStorage.setItem("user", JSON.stringify(result.user));

// Check Auth
const user = AuthAPI.getCurrentUser();
if (!user) redirectToLogin();
```

### Backend
```python
# Protected routes use JWT
@require_role("admin")
def admin_endpoint():
    # Only admins can access
    pass
```

---

## Error Handling

### Frontend Level
```javascript
try {
  response = await apiCall(...)
} catch (error) {
  showToast("Error: " + error.message, "error")
}
```

### Backend Level
```python
try:
    result = process_business_logic()
    return {"status": "success", "data": result}, 200
except ValueError:
    return {"status": "error", "code": "validation_error"}, 400
except Exception:
    return {"status": "error", "code": "internal_error"}, 500
```

### Agent Level
```python
try:
    result = run_agent(input)
except Exception as e:
    return {
        "status": "success",
        "response": "Something unexpected happened. Please try again."
    }
```

---

## Environment Setup

### .env file (Backend)
```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# VAPI
VAPI_API_KEY=your_vapi_key
VAPI_AGENT_ID=your_agent_id

# Backend
AGENT_BASE_URL=http://localhost:5000
DEBUG=True
```

### Config file (Frontend)
```javascript
// In index.html or config.js
window.API_BASE = "http://localhost:5000";
window.VAPI_PUBLIC_KEY = "your_public_key";
window.VAPI_AGENT_ID = "your_agent_id";
```

---

## Running the System

### Start Backend
```bash
cd backend
python run.py
# Starts on http://localhost:5000
```

### Open Frontend
```bash
# Option 1: Simple HTTP server
python -m http.server 8000 -d Frontend/

# Option 2: Using VS Code Live Server
# Right-click index.html → "Open with Live Server"

# Point browser to: http://localhost:8000/html/index.html
```

### Test Endpoints
```bash
# Test chat
curl -X POST http://localhost:5000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Order paracetamol", "customer_id": "PAT001"}'

# Test voice webhook
curl -X POST http://localhost:5000/chat/voice-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Check inventory", "customer_id": "VOICE_USER"}'
```

---

## Deployment

### Backend (Heroku/Railway)
```bash
git push heroku main
# Runs: gunicorn -w 4 backend.run:app
```

### Frontend (Netlify/Vercel)
```bash
# Just upload Frontend/ folder
# Or use build process if using JS framework
```

### VAPI Webhook
```
Must be HTTPS
Example: https://pharmly-app.herokuapp.com/chat/voice-webhook
```

---

## Monitoring & Debugging

### Backend Logs
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Message: %s", var)
logging.error("Error: %s", error)
```

### Frontend Logs
```javascript
console.log("Debug info:", obj);
console.error("Error:", error);
console.warn("Warning:", warning);
```

### Agent Logs
```
Check: /tmp/pharmacy_agent.log
Shows: Extraction → Controller → Responder flow
```

---

## Authentication Credentials (Demo)

### Admin Account
- Email: `admin@pharmacy.com`
- Password: `admin123`

### Clerk Account
- Email: `clerk@pharmacy.com`
- Password: `clerk123`

### Demo Customer
- ID: `PAT001`
- For voice: `VOICE_USER`

---

## Next Steps

1. ✅ Backend running
2. ✅ Frontend loaded
3. Test API endpoints
4. Configure VAPI
5. Test voice calls
6. Deploy to production
7. Monitor and optimize

For issues, check:
- Console logs (browser DevTools)
- Server logs (backend terminal)
- Agent logs (/tmp/pharmacy_agent.log)
- Network tab (browser DevTools)
