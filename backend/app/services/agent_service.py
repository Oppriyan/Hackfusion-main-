# app/services/agent_service.py

import logging
from agents.core.agent_runner import run_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# -------------------------------------------
# MAIN ORCHESTRATOR (OPENAI-DRIVEN)
# -------------------------------------------

def process_chat_message(message: str, customer_id: str = "PAT999"):
    """
    Process user message through agent pipeline
    
    Args:
        message: User input text
        customer_id: Customer identifier
        
    Returns:
        tuple: (response_dict, status_code)
    """

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
        # 🔥 Call agent pipeline
        # Extractors → Controller → Responder
        logging.info(f"🤖 Processing message from {customer_id}: {message}")
        
        agent_result = run_agent(message)

        # run_agent returns:
        # {
        #   "status": "success",
        #   "response": "text reply"
        # }

        logging.info(f"✅ Agent response: {agent_result.get('response', '')}")

        return {
            "status": "success",
            "data": {
                "reply": agent_result.get("response", ""),
                "message": message,
                "customer_id": customer_id
            }
        }, 200

    except Exception as e:
        logging.error(f"❌ Agent service error: {str(e)}")
        print(f"❌ Agent service error: {str(e)}")
        return {
            "status": "error",
            "code": "agent_error",
            "message": "Agent processing failed. Please try again."
        }, 500


def process_voice_message(message: str, customer_id: str = "PAT999"):
    """
    Process voice message (from VAPI webhook)
    Same as chat but optimized for voice interaction
    
    Args:
        message: Transcribed voice text
        customer_id: Customer identifier
        
    Returns:
        tuple: (response_dict, status_code)
    """
    logging.info(f"🎤 Processing voice message from {customer_id}: {message}")
    
    # Process through same agent pipeline
    response, status = process_chat_message(message, customer_id)
    
    if status == 200 and response.get("status") == "success":
        # Ensure response is voice-friendly (shorter, clearer)
        reply = response.get("data", {}).get("reply", "")
        
        # Log voice processing
        logging.info(f"🎤 Voice response: {reply}")
        
        # Return success with voice-specific format
        return response, status
    else:
        logging.warning(f"❌ Voice processing failed: {response}")
        return {
            "status": "error",
            "code": "voice_processing_error",
            "message": response.get("message", "Voice processing failed")
        }, status