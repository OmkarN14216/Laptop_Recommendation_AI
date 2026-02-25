import re
import ast
from groq import Groq
from app.config import get_settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

REQUIRED_KEYS = [
    'GPU intensity', 'Processing speed', 'RAM capacity',
    'Storage capacity', 'Storage type', 'Display quality',
    'Display size', 'Portability', 'Battery life', 'Budget'
]
VALID_VALUES = {'low', 'medium', 'high'}

# Fuzzy map — handles LLM slippage like "medium to high", "moderate", etc.
FUZZY_MAP = {
    'medium to high': 'high',
    'high to medium': 'high',
    'low to medium':  'medium',
    'medium to low':  'medium',
    'moderate':       'medium',
    'moderate to high': 'high',
    'very high':      'high',
    'very low':       'low',
    'minimal':        'low',
    'basic':          'low',
    'standard':       'medium',
    'good':           'medium',
    'great':          'high',
    'excellent':      'high',
}


def normalise_value(val: str) -> str:
    """Normalise a value to low/medium/high using fuzzy matching."""
    v = val.strip().lower()
    if v in VALID_VALUES:
        return v
    if v in FUZZY_MAP:
        return FUZZY_MAP[v]
    # partial match — e.g. "medium (16gb)" → "medium"
    for valid in VALID_VALUES:
        if v.startswith(valid):
            return valid
    return v  # return as-is, will fail validation


class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.1-8b-instant"

    def get_completion(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq completion error: {e}")
            return ""

    def get_chat_completion(self, messages: List[Dict]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq chat completion error: {e}")
            return ""

    def intent_confirmation_layer(self, response_assistant: str) -> bool:
        """
        Pure Python — no LLM.
        Finds the dict, normalises fuzzy values, validates all 10 keys.
        """
        match = re.search(r'\{[^{}]+\}', response_assistant, re.DOTALL)
        if not match:
            return False
        try:
            d = ast.literal_eval(match.group())
        except Exception:
            return False
        if not isinstance(d, dict):
            return False

        for key in REQUIRED_KEYS:
            # find the key case-insensitively
            val = None
            for k, v in d.items():
                if k.strip().lower() == key.lower():
                    val = str(v).strip().lower()
                    break
            if val is None:
                return False
            if key == 'Budget':
                if not re.search(r'\d+', val):
                    return False
            else:
                if normalise_value(val) not in VALID_VALUES:
                    return False
        return True

    def dictionary_present(self, response: str) -> Optional[dict]:
        """
        Pure Python — no LLM.
        Extracts, normalises and returns the requirements dict or None.
        """
        match = re.search(r'\{[^{}]+\}', response, re.DOTALL)
        if not match:
            return None
        try:
            d = ast.literal_eval(match.group())
        except Exception:
            return None
        if not isinstance(d, dict):
            return None

        result = {}
        for key in REQUIRED_KEYS:
            for k, v in d.items():
                if k.strip().lower() == key.lower():
                    raw = str(v).strip().lower()
                    result[key.lower()] = normalise_value(raw) if key != 'Budget' else re.sub(r'[^\d]', '', raw)
                    break

        return result if len(result) == len(REQUIRED_KEYS) else None

    def initialize_conversation(self) -> List[Dict]:
        system_message = """You are a friendly but thorough laptop advisor. Collect all 10 requirements before recommending.

REQUIREMENTS (collect ALL before outputting dictionary):
1. GPU intensity       → MUST be exactly: low / medium / high
2. Processing speed    → MUST be exactly: low / medium / high
3. RAM capacity        → MUST be exactly: low / medium / high
4. Storage capacity    → MUST be exactly: low / medium / high
5. Storage type        → MUST be exactly: low / medium / high
6. Display quality     → MUST be exactly: low / medium / high
7. Display size        → MUST be exactly: low / medium / high
8. Portability         → MUST be exactly: low / medium / high
9. Battery life        → MUST be exactly: low / medium / high
10. Budget             → number only in INR (e.g. 80000)

⚠️ CRITICAL: Every value in the dictionary MUST be exactly 'low', 'medium', or 'high'.
NEVER use 'medium to high', 'moderate', 'good', or any other variation.
If unsure between two levels, pick the higher one.

MAPPING GUIDE:
- GPU: gaming/ML/3D/video editing=high, photo editing/light gaming=medium, basic use=low
- Processing: i7+/Ryzen7+/heavy workloads=high, i5/Ryzen5/coding/multitasking=medium, i3/basic=low
- RAM: 32GB+=high, 16GB=medium, 8GB=low
- Storage capacity: >1TB=high, 512GB=medium, <512GB=low
- Storage type: NVMe SSD=high, SATA SSD=medium, HDD=low
- Display quality: 2K/4K/OLED=high, Full HD=medium, HD=low
- Display size: >15.6"=high, 14-15.6"=medium, <14"=low
- Portability: frequent travel/lightweight=high, occasional travel=medium, mostly at desk=low
- Battery: >10hrs=high, 6-10hrs=medium, plugged in mostly=low

CONVERSATION RULES:
1. Ask 2-3 questions per message — never ask just 1, never dump all at once
2. Vague context like "CSE student" or "some ML work" is NOT enough — you must clarify intensity
3. Always clarify: how heavy is the ML/coding work, RAM needs, portability preference, battery needs
4. Budget is mandatory — always ask if not provided
5. If user states something clearly, accept it — do not re-confirm
6. Only output the dictionary when ALL 10 values are confirmed
7. Stop completely after outputting the dictionary

ALWAYS CLARIFY UNLESS EXPLICITLY STATED:
- How intensive is the ML work? (daily model training=high GPU, occasional experiments=medium)
- RAM: 16GB or 32GB?
- Screen size preference and display quality?
- Travel frequency for portability?
- Expected battery hours per day?

FINAL OUTPUT (only when all 10 confirmed):
"Here's your complete profile:

{'GPU intensity': 'high', 'Processing speed': 'high', 'RAM capacity': 'medium', 'Storage capacity': 'medium', 'Storage type': 'high', 'Display quality': 'medium', 'Display size': 'medium', 'Portability': 'medium', 'Battery life': 'medium', 'Budget': '80000'}

Finding the best laptops for you..."

Start with a greeting and ask what they need the laptop for."""

        return [{"role": "system", "content": system_message}]


groq_service = GroqService()