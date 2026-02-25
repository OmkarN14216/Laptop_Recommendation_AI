from app.database import get_database
from typing import List, Dict, Optional
import re
import ast
import logging

logger = logging.getLogger(__name__)


class LaptopService:

    def _get_db(self):
        """Get DB instance fresh every time — no stale None reference."""
        db = get_database()
        if db is None:
            raise RuntimeError("Database not initialized. Check MongoDB connection.")
        return db

    async def get_all_laptops(self) -> List[Dict]:
        laptops = await self._get_db().laptops.find().to_list(length=None)
        for laptop in laptops:
            laptop['_id'] = str(laptop['_id'])
        return laptops

    def extract_dictionary_from_string(self, string: str) -> Optional[Dict]:
        """Kept for backward compatibility."""
        match = re.search(r'\{[^{}]+\}', string, re.DOTALL)
        if match:
            try:
                return ast.literal_eval(match.group().lower())
            except Exception as e:
                logger.error(f"Error parsing dictionary: {e}")
        return None

    async def compare_laptops_with_user(self, user_req: Dict) -> List[Dict]:
        """Compare laptops with user requirements and return top 3."""
        if not user_req:
            logger.error("Empty user requirements")
            return []

        logger.info(f"User Requirements: {user_req}")

        # Parse budget — strip everything except digits
        budget_str = str(user_req.get('budget', '0'))
        digits = re.sub(r'[^\d]', '', budget_str)
        budget = int(digits) if digits else 0
        logger.info(f"Budget: ₹{budget}")

        all_laptops = await self.get_all_laptops()
        logger.info(f"Total laptops in database: {len(all_laptops)}")

        # Filter by budget
        filtered_laptops = []
        for laptop in all_laptops:
            try:
                laptop_price = int(str(laptop['price']).replace(',', ''))
                if laptop_price <= budget:
                    filtered_laptops.append(laptop)
            except Exception:
                continue

        logger.info(f"Laptops within budget: {len(filtered_laptops)}")

        if not filtered_laptops:
            logger.warning("No laptops found within budget")
            return []

        mappings = {'low': 0, 'medium': 1, 'high': 2}
        scoreable_features = [
            'gpu intensity', 'processing speed', 'ram capacity',
            'storage capacity', 'storage type', 'display quality',
            'display size', 'portability', 'battery life'
        ]

        for laptop in filtered_laptops:
            score = 0
            laptop_feature = laptop.get('laptop_feature', {})
            match_details = {}

            if not laptop_feature:
                laptop['score'] = 0
                laptop['match_details'] = {}
                continue

            for feature in scoreable_features:
                user_val = str(user_req.get(feature, 'low')).lower()
                laptop_val = str(laptop_feature.get(feature, 'low')).lower()

                if mappings.get(laptop_val, 0) >= mappings.get(user_val, 0):
                    score += 1
                    match_details[feature] = f"✅ {laptop_val} (need: {user_val})"
                else:
                    match_details[feature] = f"❌ {laptop_val} (need: {user_val})"

            laptop['score'] = score
            laptop['match_details'] = match_details

        filtered_laptops.sort(key=lambda x: x.get('score', 0), reverse=True)
        top_laptops = filtered_laptops[:3]

        validated = [l for l in top_laptops if l.get('score', 0) >= 5]

        if not validated and top_laptops:
            logger.warning("No laptops scored ≥5, returning top 3 anyway")
            return top_laptops

        logger.info(f"Returning {len(validated)} laptops")
        return validated


logger.debug("laptop_service module loaded")
laptop_service = LaptopService()