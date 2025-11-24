from pydantic import BaseModel
from typing import Dict, List, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str
    persona: Optional[str] = "efficient"  # "confused", "chatty", "edge"

class ChatResponse(BaseModel):
    reply: str
    mode: str
    company: Optional[str] = None
    account_plan: Optional[Dict[str, str]] = None  # sections as JSON

class SessionState(BaseModel):
    mode: str = "discovery"  # discovery | research | planning | editing
    target_company: Optional[str] = None
    persona: str = "efficient"
    research_notes: List[str] = []
    account_plan: Dict[str, str] = {}