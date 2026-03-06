# agents/tools/webhook.py

import os
import uuid
import requests
from datetime import datetime
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

WEBHOOK_URL = "https://n8n.srv1403775.hstgr.cloud/webhook/pharmacy-events-v2"
WEBHOOK_TIMEOUT = 5


@traceable(name="Trigger-Automation-Webhook")
def trigger_admin_alert(event_type: str, payload: dict):

    if not WEBHOOK_URL:
        return {"status": "disabled"}

    if not event_type or not isinstance(payload, dict):
        return {"status": "invalid"}

    try:
        event_data = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "source": "pharmacy_ai_agent",
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        print("FIRING WEBHOOK TO:", WEBHOOK_URL)
        response = requests.post(
            WEBHOOK_URL,
            json=event_data,
            timeout=WEBHOOK_TIMEOUT
        )

        if 200 <= response.status_code < 300:
            return {"status": "sent"}

        return {"status": "failed", "code": response.status_code}

    except Exception:
        return {"status": "failed"}