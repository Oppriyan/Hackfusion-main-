# app/services/agent_service.py

from agents.core.agent_runner import run_agent


# -------------------------------------------
# MAIN ORCHESTRATOR (OPENAI-DRIVEN)
# -------------------------------------------

def process_chat_message(message: str):

    # -------------------------
    # Validation
    # -------------------------
    if not message or not isinstance(message, str):
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Message is required"
        }, 400

    message = message.strip()

    if not message:
        return {
            "status": "error",
            "code": "validation_error",
            "message": "Message cannot be empty"
        }, 400

    try:

        # 🔥 Call your real OpenAI agent
        agent_result = run_agent(message)

        # run_agent already returns:
        # {
        #   "status": "success",
        #   "response": "text reply"
        # }

        return {
            "status": "success",
            "data": {
                "reply": agent_result.get("response", "")
            }
        }, 200

    except Exception:
        return {
            "status": "error",
            "code": "internal_error",
            "message": "AI processing failed"
        }, 500