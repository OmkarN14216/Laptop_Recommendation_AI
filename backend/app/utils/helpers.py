import uuid
from datetime import datetime

def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def moderation_check(user_input: str) -> str:
    """Simple moderation check"""
    flagged_words = ['kill', 'harm', 'attack', 'violence', 'weapon']
    for word in flagged_words:
        if word in user_input.lower():
            return "Flagged"
    return "Not Flagged"