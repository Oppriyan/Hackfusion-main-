# app/routes/webhook.py

from flask import Blueprint, request, jsonify
from app.services.agent_service import process_chat_message

webhook_bp = Blueprint("webhook", __name__)


# -------------------------------------------
# VAPI VOICE WEBHOOK
# -------------------------------------------

@webhook_bp.route("/vapi-webhook", methods=["POST"])
def vapi_webhook():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "response": "No data received."
            }), 400

        # VAPI usually sends transcript field
        transcript = data.get("transcript") or data.get("message")

        if not transcript:
            return jsonify({
                "response": "No transcript found."
            }), 400

        # Call your existing agent orchestrator
        agent_response, status_code = process_chat_message(transcript)

        # Extract reply safely
        reply_text = agent_response.get("data", {}).get("reply") \
            if agent_response.get("status") == "success" \
            else agent_response.get("message")

        return jsonify({
            "response": reply_text
        }), status_code

    except Exception:
        return jsonify({
            "response": "Something went wrong processing your request."
        }), 500