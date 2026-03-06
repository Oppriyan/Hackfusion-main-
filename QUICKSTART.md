# Pharmly - Quick Start & Troubleshooting Guide

## Quick Start (5 minutes)

### For Windows Users

1. **Double-click** `startup.bat`
2. Two terminal windows will open (Backend & Frontend)
3. Open browser → `http://localhost:8000/html/index.html`
4. Login with:
   - Email: `admin@pharmacy.com`
   - Password: `admin123`

### For Mac/Linux Users

```bash
chmod +x startup.sh
./startup.sh
```

Then open: `http://localhost:8000/html/index.html`

### Manual Start (If Startup Script Fails)

**Terminal 1 - Backend:**
```bash
cd backend
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd Frontend
python -m http.server 8000
```

**Then open browser:**
```
http://localhost:8000/html/index.html
```

---

## Configuration

### .env File (Backend)

Create `backend/.env`:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# VAPI Voice Integration (Optional)
VAPI_API_KEY=your_vapi_key_here
VAPI_AGENT_ID=your_agent_id_here

# Database
DATABASE_PATH=data/pharmacy.db

# Agent Configuration
AGENT_BASE_URL=http://localhost:5000
DEBUG=True
LOG_LEVEL=INFO
```

### Frontend Configuration

Create `Frontend/config.js` (or add to index.html):

```javascript
// API Configuration
window.API_BASE = "http://localhost:5000";
window.API_TIMEOUT = 30000; // 30 seconds

// VAPI Voice Configuration (Optional)
window.VAPI_PUBLIC_KEY = "your_vapi_public_key";
window.VAPI_AGENT_ID = "your_agent_id";
window.VAPI_USE_TTS = true; // Use VAPI for text-to-speech

// Feature Flags
window.FEATURES = {
  enableVoice: true,
  enableChat: true,
  enablePrescriptions: true,
  enableAdmin: true
};
```

---

## Troubleshooting

### ❌ Backend Won't Start

**Error: "Address already in use"**
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :5000
kill -9 <PID>
```

**Error: "ModuleNotFoundError"**
```bash
cd backend
pip install -r requirements.txt
```

**Error: "AZURE_OPENAI_API_KEY not found"**
1. Create `backend/.env` file
2. Add your Azure OpenAI credentials
3. Restart backend

### ❌ Frontend Won't Load

**Error: "Cannot GET /html/index.html"**
- Make sure you're in `Frontend` directory before starting http.server
- Try: `python -m http.server 8000 -d Frontend/`

**Error: "Failed to fetch API"**
- Check backend is running: `http://localhost:5000/health`
- Check CORS is enabled (should be by default)
- Check firewall isn't blocking port 5000

**Error: "Cannot import api module"**
- Make sure `api.js` is in `Frontend/js/` directory
- Check all imports in `app.js` are correct

### ❌ Agent Not Responding

**Error: "Agent processing failed"**
1. Check Azure OpenAI API key is valid
2. Check deployment name matches (should be `gpt-4o`)
3. Check rate limits (Azure quota)
4. Check logs: `tail -f backend/logs/agent.log`

**Error: "Empty response from agent"**
- Backend timeout (increase in `tools.py` → timeout=5)
- Agent crashed (check backend terminal for errors)
- No valid response generated

### ❌ Database Issues

**Error: "Database is locked"**
```bash
# SQLite database locked - usually multiple writes
# Solution: Close all connections and restart backend
```

**Error: "Table medicines doesn't exist"**
```bash
# Database not initialized
# Solution: Delete `data/pharmacy.db` and restart backend
# Backend will recreate schema automatically
```

**No medicines showing in shop**
1. Check if data loaded from Excel: `backend/data/raw/` should have Excel files
2. Check `excel_loader.py` is working
3. Manually insert test data:
   ```sql
   INSERT INTO medicines (name, price, stock, prescription_required)
   VALUES ('Paracetamol', 2.06, 100, 'No');
   ```

### ❌ Voice (VAPI) Not Working

**Error: "VAPI SDK not loaded"**
- VAPI library not included in HTML
- Add to `Frontend/html/index.html`:
  ```html
  <script src="https://cdn.jsdelivr.net/npm/vapi-js"></script>
  ```

**Error: "Microphone permission denied"**
- Browser permission issue
- Allow microphone in browser settings
- Test: https://www.google.com/search?q=test+microphone

**Error: "No audio output"**
- Check speaker volume
- Check browser audio settings
- Test system audio first

**Voice webhook timeout**
- Ensure backend responds in < 5 seconds
- Check agent not hanging
- Increase timeout in `tools.py`

### ❌ Login Issues

**Error: "Invalid credentials"**
- Correct username: `admin@pharmacy.com`
- Correct password: `admin123`
- Check database has users (should be seeded)

**Error: "Session expired"**
- Clear localStorage: 
  ```javascript
  localStorage.clear()
  ```
- Login again

**Error: "Permission denied"**
- Check user role in database: `users` table
- Admin: role = 'admin'
- User: role = 'user'

### ❌ API Errors

**Error: "Prescription required for medicine"**
- Medicine ID 3 (Amoxicillin) requires Rx
- Upload prescription first at `/prescription/upload-prescription`
- Wait for admin approval

**Error: "Insufficient stock"**
- Medicine out of stock
- Adjust quantity or choose different medicine
- Admin can restock at inventory management

**Error: "CORS error"**
- Backend CORS not enabled
- Check `app/__init__.py` has:
  ```python
  CORS(app, resources={r"/*": {"origins": "*"}})
  ```

---

## Testing Workflow

### 1. Test Backend Health
```bash
curl http://localhost:5000/health
# Expected: {"status": "ok"}
```

### 2. Test Medicine Lookup
```bash
curl http://localhost:5000/inventory/Paracetamol
# Expected: List of medicines
```

### 3. Test Chat/Agent
```bash
curl -X POST http://localhost:5000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Check paracetamol stock", "customer_id": "PAT001"}'
# Expected: Natural language response
```

### 4. Test Voice Webhook
```bash
curl -X POST http://localhost:5000/chat/voice-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Order 2 paracetamol",
    "customer_id": "PAT001",
    "call_id": "test_123"
  }'
# Expected: Voice response formatted
```

### 5. Test Frontend UI
1. Open `http://localhost:8000/html/index.html`
2. Login with `admin@pharmacy.com` / `admin123`
3. Navigate to Shop → Should see medicines
4. Add to cart → Should work
5. Open Chat → Send message → Should see agent response

---

## Common Use Cases

### Use Case 1: Order Medicine via Chat

**User:** "Order 2 paracetamol"

**Steps:**
1. Chat processes message through agent
2. Agent extracts: intent=order, quantity=2, medicine=paracetamol
3. Backend checks inventory (✓ In stock)
4. Backend checks prescription (✓ No prescription required)
5. Order created
6. Response: "Order #15 created: 2x Paracetamol €4.12"

### Use Case 2: Order Prescription Medicine via Chat

**User:** "Order 1 amoxicillin"

**Steps:**
1. Agent extracts: intent=order, quantity=1, medicine=amoxicillin
2. Backend checks inventory (✓ In stock)
3. Backend checks prescription (✗ Not verified)
4. Response: "Amoxicillin requires a prescription. Please upload it first."
5. User uploads prescription via app
6. Admin approves in Admin Panel
7. User retries order → Now succeeds

### Use Case 3: Admin Approves Prescription

**Steps:**
1. Customer uploads prescription for amoxicillin
2. Status shows "Pending"
3. Admin goes to Admin Panel
4. Sees pending prescription
5. Clicks "Approve"
6. Prescription marked "Approved" + valid for 30 days
7. Customer can now order amoxicillin

---

## Performance Tips

### Backend
- Use `gunicorn` in production (handles concurrency)
- Set `WORKERS = 4` for standard VPS
- Cache medicine list (rarely changes)
- Use connection pooling for database

### Frontend
- Lazy load images
- Cache API responses
- Use service workers
- Minimize JavaScript

### Agent
- Use fallback parser if Azure is slow
- Cache intent extraction for common phrases
- Use shorter timeouts on slow networks
- Batch operations when possible

---

## Security Checklist

□ Change default passwords (admin@pharmacy.com)
□ Use HTTPS in production
□ Validate all user inputs
□ Enable CSRF protection
□ Rate limit API endpoints
□ Encrypt sensitive data
□ Audit prescription approvals
□ Log all transactions
□ Regular backups of database
□ Monitor for suspicious activity

---

## Support & Debugging

### Enable Detailed Logging

**Backend:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```javascript
// In browser console
localStorage.setItem('DEBUG', 'true');
```

### Check Logs

**Backend logs:**
```bash
tail -f backend/logs/pharmacy.log
```

**Agent logs:**
```bash
cat /tmp/pharmacy_agent.log
```

**Browser console:**
- F12 → Console tab
- Look for red errors
- Check Network tab for failed requests

### Debug Mode

```python
# In backend/app/__init__.py
app.run(debug=True)
```

---

## Next Steps After Setup

1. **Populate medicines** - Load data from Excel or import manually
2. **Create test prescriptions** - Upload Rx files for testing
3. **Configure VAPI** - Set up voice AI (optional)
4. **Test all workflows** - Go through each use case
5. **Deploy to production** - Use Heroku/Railway/VPS
6. **Set up monitoring** - Track errors and performance
7. **Train team** - Show staff how to use admin panel

---

## Quick Reference

| Task | Command |
|------|---------|
| Start everything | `./startup.sh` or `startup.bat` |
| Backend only | `cd backend && python run.py` |
| Frontend only | `cd Frontend && python -m http.server 8000` |
| Check backend | `curl http://localhost:5000/health` |
| Reset database | `rm data/pharmacy.db && restart` |
| View logs | `tail -f backend/logs/*.log` |
| Clear cache | `localStorage.clear()` in console |
| Test API | Use Postman or curl (see examples above) |

---

For more help:
- Check INTEGRATION_GUIDE.md for architecture
- Check VAPI_INTEGRATION.md for voice setup
- Check backend/README.md for API docs
- Check logs for error details

Good luck! 🚀
