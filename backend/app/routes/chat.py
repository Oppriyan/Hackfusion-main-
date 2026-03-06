from flask import Blueprint, request, jsonify
from app.services.agent_service import process_chat_message, process_voice_message

chat_bp = Blueprint("chat", __name__)


# ============================================================
# TEXT CHAT ENDPOINT
# ============================================================

@chat_bp.route("/message", methods=["POST"])
def chat_message():
    """Send text message to agent"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body required"
            }), 400

        message = data.get("message")
        customer_id = data.get("customer_id", "PAT999")

        if not message:
            return jsonify({
                "status": "error",
                "message": "Message is required"
            }), 400

        # Process through agent pipeline
        response, status = process_chat_message(message, customer_id)

        return jsonify(response), status

    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Chat endpoint failed"
        }), 500


# ============================================================
# VOICE WEBHOOK (VAPI INTEGRATION)
# ============================================================

@chat_bp.route("/voice-webhook", methods=["POST"])
def voice_webhook():
    """
    VAPI voice AI webhook endpoint
    Receives transcribed speech and returns spoken response
    
    Expected payload:
    {
        "message": "transcribed text",
        "customer_id": "optional",
        "call_id": "optional"
    }
    
    Response format ready for VAPI playback:
    {
        "status": "success",
        "message": "spoken response",
        "call_id": "call_id",
        "customer_id": "customer_id",
        "type": "voice_response"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body required"
            }), 400

        # Extract voice data from VAPI
        message = data.get("message") or data.get("transcript")
        customer_id = data.get("customer_id", "VOICE_USER")
        call_id = data.get("call_id")

        if not message:
            return jsonify({
                "status": "error",
                "message": "No message or transcript found"
            }), 400

        print(f"🎤 Voice message from {customer_id}: {message}")

        # Process message through agent
        response, status = process_voice_message(message, customer_id)

        if status == 200 and response.get("status") == "success":
            # Format for voice response (VAPI expects specific format)
            reply = response.get("data", {}).get("reply", "I didn't understand that.")

            return jsonify({
                "status": "success",
                "message": reply,
                "call_id": call_id,
                "customer_id": customer_id,
                "type": "voice_response"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": response.get("message", "Processing failed")
            }), 500

    except Exception as e:
        print(f"❌ Voice webhook error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Voice processing failed"
        }), 500


# ============================================================
# CONVERSATION HISTORY (Optional)
# ============================================================

@chat_bp.route("/history", methods=["POST"])
def conversation_history():
    """Get conversation history for customer"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body required"
            }), 400

        customer_id = data.get("customer_id", "PAT999")

        # For now, return empty (can be extended with actual history storage)
        return jsonify({
            "status": "success",
            "data": [],
            "message": "No conversation history yet"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "History fetch failed"
        }), 500

