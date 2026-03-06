# VAPI Voice AI Integration Guide

## Overview
This file documents the integration between Pharmly and VAPI (Voice AI Platform) for voice-enabled pharmacy assistance.

---

## Architecture

```
User (Voice Call) 
    ↓
VAPI AI Platform (Speech-to-Text)
    ↓
POST /chat/voice-webhook (Pharmly Backend)
    ↓
Agent Pipeline (Extractor → Controller → Responder)
    ↓
Text Response
    ↓
VAPI (Text-to-Speech)
    ↓
User (Spoken Response)
```

---

## VAPI Webhook Configuration

### Webhook URL
```
https://your-domain.com/chat/voice-webhook
```

### HTTP Method
```
POST
```

### Expected Request Payload from VAPI
```json
{
  "message": "I want to order paracetamol",
  "transcript": "I want to order paracetamol",
  "customer_id": "PAT001",
  "call_id": "call_12345",
  "phone": "+49-151-0001",
  "speaker": "user",
  "timestamp": "2026-03-06T11:00:00Z"
}
```

### Expected Response to VAPI
```json
{
  "status": "success",
  "message": "Paracetamol 500mg is available for €2.06. Would you like to order?",
  "call_id": "call_12345",
  "customer_id": "PAT001",
  "type": "voice_response"
}
```

---

## Backend Endpoint Details

### Endpoint: `/chat/voice-webhook`

**Method:** `POST`

**Headers:** 
```
Content-Type: application/json
```

**Body:**
```json
{
  "message": "user speech transcript",
  "customer_id": "PAT001",
  "call_id": "call_id_from_vapi"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Natural language response",
  "call_id": "call_id_from_vapi",
  "customer_id": "PAT001",
  "type": "voice_response"
}
```

---

## Integration Steps

### 1. VAPI Dashboard Setup

1. Log into VAPI dashboard
2. Navigate to **Assistants** → **Create New**
3. Configure:
   - **Name:** Pharmly Voice Assistant
   - **Model:** GPT-4o (or GPT-3.5-turbo)
   - **Voice:** Any (e.g., ElevenLabs - Amara)
   - **Webhook URL:** `https://your-domain.com/chat/voice-webhook`
   - **Webhook Type:** POST

### 2. System Prompt (Configure in VAPI)

```
You are Pharmly, an AI pharmacy assistant. You help customers with:
- Medicine orders
- Inventory checks
- Prescription uploads
- Order history

Always be helpful, professional, and concise. Confirm details before taking action.
```

### 3. Backend Configuration (.env file)

```env
# VAPI Configuration
VAPI_API_KEY=your_vapi_api_key
VAPI_WEBHOOK_SECRET=your_webhook_secret

# Voice to Text (handled by VAPI)
# Text to Speech (handled by VAPI)

# Backend
AGENT_BASE_URL=http://localhost:5000
```

### 4. Secure the Webhook (Optional)

Add signature verification:

```python
import hmac
import hashlib

def verify_vapi_signature(request, webhook_secret):
    signature = request.headers.get("X-VAPI-Signature")
    body = request.get_data()
    
    expected_signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

---

## Voice Commands Examples

### Order a Medicine
```
"I want to order 2 paracetamol"
→ "I'll create an order for 2 units of Paracetamol 500mg. 
   This will cost €4.12 total. Is that correct?"
```

### Check Inventory
```
"Do you have ibuprofen in stock?"
→ "Yes, we have 5 units of Ibuprofen 200mg (Nurofen) available for €10.98 each."
```

### Upload Prescription
```
"I need to upload a prescription for amoxicillin"
→ "Please upload your prescription file through the app. 
   Once approved by our pharmacist, you can order."
```

### Check Order Status
```
"What's the status of order 15?"
→ "Order #15 is confirmed. Medicine: Paracetamol, 
   Quantity: 2, Total: €4.12. Expected delivery: 24 hours."
```

---

## Frontend Integration

### JavaScript Handler

```javascript
// In modules/chatbot.js

export async function initVoiceChat() {
  // Initialize VAPI SDK (if available)
  if (window.VAPI) {
    VAPI.init({
      apiKey: 'your_vapi_public_key',
      agentId: 'your_agent_id'
    });
    
    window.startVoiceCall = function() {
      VAPI.start();
    };
    
    window.stopVoiceCall = function() {
      VAPI.stop();
    };
  }
}
```

### HTML Integration

```html
<!-- Add voice button to chatbot interface -->
<button id="voiceBtn" class="btn-voice" onclick="startVoiceCall()">
  🎤 Start Voice Call
</button>

<!-- Or use embedded VAPI widget -->
<script src="https://cdn.jsdelivr.net/npm/vapi-js"></script>
```

---

## Error Handling

### Timeout
If VAPI doesn't receive response within 30 seconds, call is disconnected.

**Solution:** Ensure backend response time < 5 seconds

### No Transcript
If speech is unclear, VAPI requests repetition.

**Solution:** Agent handles gracefully with fallback response

### Webhook Failure
If webhook returns error status, VAPI returns to user.

**Solution:** Implement robust error handling in backend

---

## Debugging

### Enable Voice Logs

In `.env`:
```
LOG_LEVEL=DEBUG
VAPI_DEBUG=true
```

### Test Webhook Locally

```bash
curl -X POST http://localhost:5000/chat/voice-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Order paracetamol",
    "customer_id": "PAT001",
    "call_id": "test_call_123"
  }'
```

### Monitor in Real-time

```python
# In backend, add logging to voice_webhook()
print(f"🎤 VAPI Webhook called")
print(f"📝 Message: {message}")
print(f"👤 Customer: {customer_id}")
print(f"📞 Call ID: {call_id}")
```

---

## Cost Estimation

**Per Call:**
- Speech-to-Text: $0.01-0.05 (VAPI pricing)
- Agent Processing: $0.001-0.01 (OpenAI API)
- Text-to-Speech: $0.01-0.05 (VAPI pricing)
- **Total: ~$0.03-0.15 per call**

---

## Production Deployment

### HTTPS Required
```
VAPI only accepts HTTPS webhooks
Ensure SSL certificate is valid
```

### Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@chat_bp.route("/voice-webhook", methods=["POST"])
@limiter.limit("100/hour")
def voice_webhook():
    # ...
```

### Monitoring
- Track voice call success rate
- Monitor average response time
- Alert on webhook failures
- Log all conversations (with privacy compliance)

---

## Privacy & Compliance

### GDPR Compliance
- Customer consent for voice recording required
- Secure storage of voice data
- Right to deletion implemented

### HIPAA Compliance (if applicable)
- Encrypt voice data in transit (HTTPS)
- Encrypt voice data at rest
- Maintain audit logs
- Business associate agreement (BAA) with VAPI

---

## Next Steps

1. Get VAPI API Key from dashboard
2. Configure webhook in VAPI settings
3. Deploy backend to production
4. Test with real voice calls
5. Monitor and optimize

For support: support@vapi.ai or visit https://vapi.ai
