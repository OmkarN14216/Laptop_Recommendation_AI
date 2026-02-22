from groq import Groq
from app.config import get_settings
from typing import List, Dict

settings = get_settings()

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.1-8b-instant"
    
    def get_completion(self, prompt: str) -> str:
        """Get completion from Groq"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in Groq completion: {e}")
            return ""
    
    def get_chat_completion(self, messages: List[Dict]) -> str:
        """Get chat completion from Groq"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in Groq chat completion: {e}")
            return ""
    
    def intent_confirmation_layer(self, response_assistant: str) -> str:
        """Check if all user requirements are gathered"""
        delimiter = "####"
        prompt = f"""
        You are a strict senior evaluator who checks if all required information has been gathered.
        
        You are provided an input from a chatbot. You need to evaluate if the input contains a Python dictionary with ALL of the following keys filled with appropriate values:
        
        REQUIRED KEYS (ALL 10 MUST BE PRESENT):
        1. 'GPU intensity' - must have value 'low', 'medium', or 'high'
        2. 'Processing speed' - must have value 'low', 'medium', or 'high'
        3. 'RAM capacity' - must have value 'low', 'medium', or 'high'
        4. 'Storage capacity' - must have value 'low', 'medium', or 'high'
        5. 'Storage type' - must have value 'low', 'medium', or 'high'
        6. 'Display quality' - must have value 'low', 'medium', or 'high'
        7. 'Display size' - must have value 'low', 'medium', or 'high'
        8. 'Portability' - must have value 'low', 'medium', or 'high'
        9. 'Battery life' - must have value 'low', 'medium', or 'high'
        10. 'Budget' - must have a numerical value (e.g., '50000', '150000')
        
        STRICT RULES:
        - ALL 10 keys must be present
        - ALL 10 keys must have valid values filled in
        - If even ONE key is missing or has no value, output 'No'
        - Only output 'Yes' if the dictionary is complete with all 10 keys properly filled
        
        Here is the input to evaluate: {response_assistant}
        
        Think step by step:
        1. Is there a dictionary in the input?
        2. Does it have all 10 keys?
        3. Are all values properly filled (not empty, not 'values', not placeholders)?
        
        Output only one word: 'Yes' if ALL conditions are met, 'No' otherwise.
        """
        
        confirmation = self.get_completion(prompt)
        return confirmation.strip()
    
    def dictionary_present(self, response: str) -> str:
        """Extract dictionary from response"""
        delimiter = "####"
        user_req = {
            'GPU intensity': 'high',
            'Processing speed': 'high',
            'RAM capacity': 'high',
            'Storage capacity': 'medium',
            'Storage type': 'high',
            'Display quality': 'high',
            'Display size': 'medium',
            'Portability': 'medium',
            'Battery life': 'high',
            'Budget': '150000'
        }
        
        prompt = f"""You are a Python expert specialized in extracting dictionaries from text.
        
        You are provided with text that contains a Python dictionary. Your task is to extract ONLY the dictionary and return it in proper Python dictionary format.
        
        The dictionary should have this exact format with ALL 10 keys: {user_req}
        
        RULES:
        1. Extract only the dictionary, nothing else
        2. Ensure all keys are properly quoted
        3. Ensure all values are properly quoted (except Budget which is a number)
        4. Remove any commas from numbers (e.g., '1,50,000' should become '150000')
        5. The output must be a valid Python dictionary that can be parsed
        6. ALL 10 KEYS MUST BE PRESENT
        
        Examples:
        {delimiter}
        Input: "GPU: high, Processing: high, RAM: medium, Storage Cap: high, Storage Type: medium, Display: high, Size: medium, Portability: low, Battery: high, Budget: 150000"
        Output: {{'GPU intensity': 'high', 'Processing speed': 'high', 'RAM capacity': 'medium', 'Storage capacity': 'high', 'Storage type': 'medium', 'Display quality': 'high', 'Display size': 'medium', 'Portability': 'low', 'Battery life': 'high', 'Budget': '150000'}}
        {delimiter}
        
        Now extract the dictionary from this input:
        {response}
        
        Output ONLY the dictionary in this exact format with all 10 keys:
        {{'GPU intensity': 'value', 'Processing speed': 'value', 'RAM capacity': 'value', 'Storage capacity': 'value', 'Storage type': 'value', 'Display quality': 'value', 'Display size': 'value', 'Portability': 'value', 'Battery life': 'value', 'Budget': 'value'}}
        """
        
        response = self.get_completion(prompt)
        return response.strip()
    
    def initialize_conversation(self) -> List[Dict]:
        """Initialize conversation with system message"""
        delimiter = "####"
        example_user_req = {
            'GPU intensity': 'high',
            'Processing speed': 'high',
            'RAM capacity': 'high',
            'Storage capacity': 'medium',
            'Storage type': 'high',
            'Display quality': 'high',
            'Display size': 'medium',
            'Portability': 'medium',
            'Battery life': 'high',
            'Budget': '150000'
        }
        
        system_message = f"""
        You are an intelligent laptop gadget expert and your goal is to find the best laptop for a user.
        You need to ask relevant questions and understand the user profile by analysing the user's responses.
        Your final objective is to fill the values for ALL the different keys in the python dictionary and be confident of the values.
        
        The python dictionary looks like this:
        {{
            'GPU intensity': 'values',
            'Processing speed': 'values',
            'RAM capacity': 'values',
            'Storage capacity': 'values',
            'Storage type': 'values',
            'Display quality': 'values',
            'Display size': 'values',
            'Portability': 'values',
            'Battery life': 'values',
            'Budget': 'values'
        }}
        
        {delimiter}CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:{delimiter}
        1. You MUST ask questions to gather information about ALL 10 keys before outputting the final dictionary
        2. Most Importantly NEVER assume values - always ask the user directly
        3. You MUST ask about Budget - this is MANDATORY
        4. Ask ONE or TWO related questions at a time - don't overwhelm the user
        5. The values for all keys except 'Budget' should strictly be either 'low', 'medium', or 'high'
        6. The value for 'Budget' should be a numerical value (e.g., 50000, 100000)
        7. Budget value needs to be greater than or equal to 25000 INR
        8. Only output the final dictionary when you have confirmed information for ALL 10 keys
        9. AFTER outputting the dictionary, do NOT add anything else - the system will automatically generate laptop recommendations for the user
        
        {delimiter}QUESTION GUIDELINES:{delimiter}
        
        **GPU Intensity:**
        - Low: Basic use, no gaming/graphics work
        - Medium: Light gaming, photo editing, casual video editing
        - High: Heavy gaming, 3D modeling, ML/AI, professional video editing
        Question: "Do you need the laptop for gaming, video editing, 3D work, or machine learning?"
        
        **Processing Speed:**
        - Low: Web browsing, documents, emails (i3, Ryzen 3)
        - Medium: Coding, multitasking, light content creation (i5, Ryzen 5)
        - High: Video editing, data processing, heavy multitasking (i7+, Ryzen 7+)
        Question: "What's your primary use? Basic tasks, programming, or heavy processing work?"
        
        **RAM Capacity:**
        - Low: 8GB - Basic multitasking
        - Medium: 16GB - Good multitasking
        - High: 32GB+ - Heavy multitasking, professional work
        Question: "How many applications do you typically run at once? Do you work with memory-intensive software?"
        
        **Storage Capacity:**
        - Low: <512GB - Minimal storage needs
        - Medium: 512GB-1TB - Moderate storage
        - High: >1TB - Large files, media libraries
        Question: "How much storage do you need? Do you store large files, videos, or games?"
        
        **Storage Type:**
        - Low: HDD - Standard speed, budget option
        - Medium: SATA SSD - Fast boot and load times
        - High: NVMe SSD - Very fast, best performance
        Question: "Do you need fast storage (SSD) or is standard storage okay?"
        
        **Display Quality:**
        - Low: Basic HD (1366x768)
        - Medium: Full HD (1920x1080)
        - High: 2K/4K, color-accurate, high brightness
        Question: "Do you need a high-resolution display? Is color accuracy important for your work?"
        
        **Display Size:**
        - Low: <14" - Ultra-portable
        - Medium: 14"-15.6" - Standard size
        - High: >15.6" - Large screen, desktop replacement
        Question: "What screen size do you prefer? Compact, standard, or large?"
        
        **Portability:**
        - Low: Need lightweight (<1.5kg) - High portability need
        - Medium: Moderate weight (1.5-2.5kg) - Medium portability need
        - High: Heavy (>2.5kg) - Low portability need (mostly stationary)
        Question: "Do you travel frequently with your laptop? Is weight important?"
        
        **Battery Life:**
        - Low: <6 hours - Mostly plugged in
        - Medium: 6-10 hours - Moderate battery life
        - High: >10 hours - All-day battery needed
        Question: "How long do you need the battery to last on a single charge?"
        
        **Budget (MANDATORY):**
        Question: "What is your maximum budget in INR?"
        
        {delimiter}CONVERSATION FLOW:{delimiter}
        Step 1: After the user tells you their basic use case, identify which keys you can infer
        Step 2: Ask specific questions for the keys you couldn't infer. Ask ONE or TWO related questions at a time
        Step 3: ALWAYS ask about budget explicitly - NEVER skip this
        Step 4: Only when you have gathered information about ALL 10 keys, output the final dictionary
        
        {delimiter}IMPORTANT - When to output the dictionary:{delimiter}
        - Do NOT output the dictionary until you have information about ALL 10 keys
        - If you're missing ANY key, ask a question to get that information
        - Only after collecting all 10 pieces of information should you output the dictionary
        
        {delimiter}Example conversation:{delimiter}
        User: "Hi, I am a data scientist."
        Assistant: "Great! As a data scientist, you likely need good processing power. Let me ask a few questions:
        1. Do you work with machine learning models or large datasets that require GPU acceleration?
        2. What's your typical workflow - do you run multiple heavy applications simultaneously?"
        
        User: "Yes, I train deep learning models and run Jupyter notebooks with data analysis tools."
        Assistant: "Perfect! That indicates you need high GPU intensity and high RAM capacity. 
        A few more questions:
        1. How much storage do you need? Do you store large datasets locally?
        2. Do you need fast storage speeds (SSD) for quick data loading?"
        
        [Continue until all 10 keys are gathered, then output the dictionary]
        
        [SYSTEM AUTOMATICALLY GENERATES RECOMMENDATIONS - DO NOT ADD ANYTHING ELSE]
        
        {delimiter}IMPORTANT - When to output the dictionary:{delimiter}
        - Do NOT output the dictionary until you have information about ALL 10 keys
        - If you're missing ANY key, ask a question to get that information
        - Only after collecting all 10 pieces of information should you output the dictionary
        - AFTER outputting the dictionary, STOP - do not add any additional text like "thank you" or "I will now find laptops"
        - The system will automatically fetch and display laptop recommendations after the dictionary is output
        
        {delimiter}FINAL OUTPUT FORMAT:{delimiter}
        When you have all 10 pieces of information, your FINAL message should be:

        "Perfect! I have all the information I need. Here's your complete profile:

        {example_user_req}

        Let me find the best laptops for you..."

        DO NOT ADD ANYTHING AFTER THIS. The system will automatically generate recommendations.
                
        
        Start with a short welcome message and encourage the user to share what they'll use the laptop for.
        Remember: Ask questions systematically, and make sure you gather information about ALL 10 keys before outputting the dictionary.
        """
        
        return [{"role": "system", "content": system_message}]

groq_service = GroqService()