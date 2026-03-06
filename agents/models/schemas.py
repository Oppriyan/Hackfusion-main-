# agents/models/schemas.py

from pydantic import BaseModel
from typing import Optional


class StructuredRequest(BaseModel):
    intent: str
    medicine_name: Optional[str] = None
    quantity: Optional[int] = None
    delta: Optional[int] = None
    customer_id: Optional[str] = None