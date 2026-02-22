from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    intent_confirmed: bool = False
    user_profile: Optional[dict] = None
    recommendations: Optional[List[dict]] = None

class SessionCreate(BaseModel):
    pass

class SessionResponse(BaseModel):
    session_id: str
    message: str