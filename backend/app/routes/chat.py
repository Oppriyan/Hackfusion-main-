from flask import Blueprint, request, jsonify
from agents.core.agent_runner import run_agent

chat_bp = Blueprint("chat", __name__)
import os
print("AZURE KEY:", os.getenv("AZURE_OPENAI_API_KEY"))
@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body required"
            }), 400

        message = data.get("message")

        if not message:
            return jsonify({
                "status": "error",
                "message": "Message is required"
            }), 400

        # 🔥 CALL AGENT DIRECTLY
        print("📩 Incoming message:", message)
        result = run_agent(message)

        # Return only clean message to UI
        return jsonify({
            "message": result.get("response", "No response generated")
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Chat endpoint failed"
        }), 500