from app.database import get_database
from typing import List, Dict, Optional
import re
import ast

class LaptopService:
    def __init__(self):
        self.db = None
    
    async def initialize(self):
        self.db = get_database()
    
    async def get_all_laptops(self) -> List[Dict]:
        """Get all laptops from database"""
        laptops = await self.db.laptops.find().to_list(length=None)
        for laptop in laptops:
            laptop['_id'] = str(laptop['_id'])
        return laptops
    
    def extract_dictionary_from_string(self, string: str) -> Optional[Dict]:
        """Extract dictionary from string"""
        regex_pattern = r"\{[^{}]+\}"
        dictionary_matches = re.findall(regex_pattern, string)
        
        if dictionary_matches:
            try:
                dictionary_string = dictionary_matches[0]
                dictionary_string = dictionary_string.lower()
                dictionary = ast.literal_eval(dictionary_string)
                return dictionary
            except Exception as e:
                print(f"Error parsing dictionary: {e}")
                return None
        return None
    
    async def compare_laptops_with_user(self, user_req_string: str) -> List[Dict]:
        """Compare laptops with user requirements and return top 3"""
        user_requirements = self.extract_dictionary_from_string(user_req_string)
        
        if not user_requirements:
            print("❌ Could not extract user requirements")
            return []
        
        print(f"✅ User Requirements: {user_requirements}")
        
        # Extract budget
        budget_str = str(user_requirements.get('budget', '0'))
        budget = int(budget_str.replace(',', '').split()[0])
        print(f"💰 Budget: ₹{budget}")
        
        # Get all laptops
        all_laptops = await self.get_all_laptops()
        print(f"📊 Total laptops in database: {len(all_laptops)}")
        
        # Filter by budget first
        filtered_laptops = []
        for laptop in all_laptops:
            try:
                laptop_price = int(str(laptop['price']).replace(',', ''))
                if laptop_price <= budget:
                    filtered_laptops.append(laptop)
            except Exception as e:
                print(f"⚠️ Error parsing price for {laptop.get('brand', 'Unknown')}: {e}")
                continue
        
        print(f"💵 Laptops within budget: {len(filtered_laptops)}")
        
        if not filtered_laptops:
            print("❌ No laptops found within budget")
            return []
        
        # Mapping system: low=0, medium=1, high=2
        mappings = {
            'low': 0,
            'medium': 1,
            'high': 2
        }
        
        # List of features to score (9 features, excluding budget)
        scoreable_features = [
            'gpu intensity',
            'processing speed',
            'ram capacity',
            'storage capacity',
            'storage type',
            'display quality',
            'display size',
            'portability',
            'battery life'
        ]
        
        # Score each laptop
        print("\n🎯 Scoring laptops...")
        for laptop in filtered_laptops:
            score = 0
            laptop_feature = laptop.get('laptop_feature', {})
            
            # Check if laptop has features
            if not laptop_feature:
                print(f"⚠️ {laptop['brand']} {laptop['model_name']} - No features found")
                laptop['score'] = 0
                laptop['match_details'] = {}
                continue
            
            match_details = {}
            
            # Calculate score for each feature
            for feature in scoreable_features:
                user_value = user_requirements.get(feature, 'low')
                laptop_value = laptop_feature.get(feature, 'low')
                
                # Convert to numeric
                laptop_mapping = mappings.get(str(laptop_value).lower(), 0)
                user_mapping = mappings.get(str(user_value).lower(), 0)
                
                # Check if laptop meets or exceeds requirement
                meets_requirement = laptop_mapping >= user_mapping
                
                if meets_requirement:
                    score += 1
                    match_details[feature] = f"✅ {laptop_value} (need: {user_value})"
                else:
                    match_details[feature] = f"❌ {laptop_value} (need: {user_value})"
            
            laptop['score'] = score
            laptop['match_details'] = match_details
            
            print(f"  {laptop['brand']} {laptop['model_name']}: Score {score}/9")
        
        # Sort by score (highest first)
        filtered_laptops.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Get top 3
        top_laptops = filtered_laptops[:3]
        
        print(f"\n🏆 Top 3 laptops:")
        for i, laptop in enumerate(top_laptops):
            print(f"  {i+1}. {laptop['brand']} {laptop['model_name']} - Score: {laptop['score']}/9, Price: ₹{laptop['price']}")
        
        # Only return laptops with score >= 5 (meets at least 5 out of 9 requirements)
        validated_laptops = [laptop for laptop in top_laptops if laptop.get('score', 0) >= 5]
        
        # If no laptops meet the threshold, return top 3 anyway with lower scores
        if not validated_laptops and top_laptops:
            print(f"⚠️ No laptops scored ≥5, returning top 3 with lower scores")
            return top_laptops
        
        print(f"✅ Returning {len(validated_laptops)} validated laptops")
        return validated_laptops

laptop_service = LaptopService()