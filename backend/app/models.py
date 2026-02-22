from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Laptop(BaseModel):
    brand: str
    model_name: str
    core: str
    cpu_manufacturer: str
    clock_speed: str
    ram_size: str
    storage_type: str
    display_type: str
    display_size: str
    graphics_processor: str
    screen_resolution: str
    os: str
    laptop_weight: str
    special_features: str
    warranty: str
    average_battery_life: str
    price: int
    description: str
    laptop_feature: Optional[dict] = None

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    session_id: str
    conversation: List[ConversationMessage] = []
    user_profile: Optional[dict] = None
    recommendations: Optional[List[dict]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)