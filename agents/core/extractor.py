# agents/core/extractor.py

import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from langsmith import traceable
from agents.models.schemas import StructuredRequest

load_dotenv()

ALLOWED_INTENTS = {
    "order",
    "inventory",
    "history",
    "upload_prescription",
    "smalltalk"
}

# --------------------------------------------------
# GROQ CLIENT
# --------------------------------------------------

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url=os.getenv("GROQ_BASE_URL")
)


@traceable(name="Intent-Extraction")
def extract_structured_request(user_input: str) -> StructuredRequest:

    if not user_input or not isinstance(user_input, str):
        return StructuredRequest(intent="smalltalk")

    user_input = user_input.strip()

    if len(user_input) > 200:
        return StructuredRequest(intent="smalltalk")

    user_input_lower = user_input.lower()

    system_prompt = """
You are a pharmacy intent extractor.

Return ONLY JSON in this format:

{
"intent": "order | inventory | history | upload_prescription | smalltalk",
"medicine_name": string or null,
"quantity": integer or null,
"customer_id": string or null
}

Return ONLY raw JSON. No explanation.
"""

    try:

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        json_match = re.search(r"\{.*\}", content, re.DOTALL)

        if json_match:
            content = json_match.group(0)

        parsed = json.loads(content)

        intent = parsed.get("intent", "smalltalk")

        if intent not in ALLOWED_INTENTS:
            intent = "smalltalk"

        quantity = parsed.get("quantity")

        try:
            quantity = int(quantity) if quantity else None
        except Exception:
            quantity = None

        return StructuredRequest(
            intent=intent,
            medicine_name=parsed.get("medicine_name"),
            quantity=quantity,
            customer_id=parsed.get("customer_id")
        )

    except Exception as e:

        print("⚠ Groq extractor failed. Using fallback parser.")
        print(str(e))

        order_match = re.search(r"order\s+(\d+)\s+([a-zA-Z\s]+)", user_input_lower)

        if order_match:

            medicine = order_match.group(2).strip()
            medicine = medicine.replace(".", "").replace(",", "")

            return StructuredRequest(
                intent="order",
                medicine_name=medicine,
                quantity=int(order_match.group(1)),
                customer_id=None
            )

        if "inventory" in user_input_lower or "stock" in user_input_lower:

            medicine = re.sub(
                r"(check|inventory|stock|of)",
                "",
                user_input_lower
            ).strip()

            medicine = medicine.replace(".", "").replace(",", "")

            return StructuredRequest(
                intent="inventory",
                medicine_name=medicine,
                quantity=None,
                customer_id=None
            )

        if "history" in user_input_lower:
            return StructuredRequest(intent="history")

        if "upload" in user_input_lower:
            return StructuredRequest(intent="upload_prescription")

        return StructuredRequest(intent="smalltalk")