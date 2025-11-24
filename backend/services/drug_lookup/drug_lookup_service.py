"""
Drug Lookup Service - Coordinates drug lookup
"""
from typing import List, Optional, Dict
from backend.services.drug_lookup.rxnorm_service import RxNormService
from backend.api.dependencies import get_drug_database
from rapidfuzz import fuzz
import re


class DrugLookupService:
    """Coordinates drug lookup from database or API."""
    
    def __init__(self):
        self.rxnorm_service = RxNormService()
        self.database = get_drug_database()
    
    # ==================== PUBLIC API ====================
    
    async def lookup_drug(
        self,
        brand_name: str,
        dosage: Optional[str] = None,
        route: Optional[str] = None,
        form: Optional[str] = None
    ) -> Dict:
        """Look up and match drug products."""
        if not brand_name or not brand_name.strip():
            return {
                "status": "invalid_input",
                "product": None,
                "products": []
            }
        
        brand_name = brand_name.strip()
        
        # Get products (from cache or API)
        products = await self._fetch_products(brand_name)
        
        if not products:
            return {
                "status": "not_found",
                "product": None,
                "products": []
            }
        
        # Filter by user criteria using fuzzy matching
        refined = self.refine_products(
            products, brand_name, dosage, route, form
        )
        
        # Decide what to return
        return self._evaluate_results(refined, products)
    
    # ==================== DATA FETCHING ====================
    
    async def _fetch_products(self, brand_name: str) -> List:
        """Get products from database or API."""
        # Check database first
        cached = self.database.get_products_by_brand(brand_name)
        if cached:
            return cached
        
        # Fetch from API
        result = await self.rxnorm_service.get_drug_details(brand_name)
        
        if result and result.get("products"):
            # Save to database
            for product in result["products"]:
                self.database.save_product(
                    rxcui=product["rxcui"],
                    brand_name=brand_name,
                    product_name=product["name"]
                )
            return result["products"]
        
        return []
    
    # ==================== MATCHING LOGIC ====================
    
    def refine_products(
    self,
    products: List[Dict],
    brand_name: Optional[str],
    dosage: Optional[str] = None,
    route: Optional[str] = None,
    form: Optional[str] = None
) -> List[Dict]:
        """Filter products using adaptive fuzzy matching."""
        if not products:
            return products
        
        if not any([dosage, route, form]):
            return products
        
        query_parts = []
        if brand_name:
            query_parts.append(brand_name)
        if dosage:
            query_parts.append(dosage)
        if form:
            query_parts.append(form)
        if route:
            query_parts.append(route)
        
        query = " ".join(query_parts)
        query_normalized = self._normalize(query)
        
        scored = []
        for product in products:
            name = product.get("name") or product.get("product_name", "")
            name_normalized = self._normalize(name)
            
            score = fuzz.token_sort_ratio(query_normalized, name_normalized)
            scored.append((product, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top_score = scored[0][1]
        
        # If top score is poor, return all
        if top_score < 60:
            return products
        
        # If perfect match (100), return ONLY that
        if top_score == 100:
            return [p for p, s in scored if s == 100]
        
        # Otherwise, return products within 10 points of top
        best_matches = [p for p, s in scored if s >= top_score - 10]
        
        return best_matches
    
    def _normalize(self, text: str) -> str:
        """Normalize text for consistent matching."""
        text = text.lower()
        # Normalize spacing
        text = re.sub(r'\s+', ' ', text)
        # Normalize concentration format: "40mg/ml" → "40 mg ml"
        text = re.sub(r'(\d+\.?\d*)\s*mg\s*/\s*ml', r'\1 mg ml', text)
        # Normalize dose format: "200mg" → "200 mg"
        text = re.sub(r'(\d+\.?\d*)\s*mg\b', r'\1 mg', text)
        return text.strip()
    
    # ==================== RESULT EVALUATION ====================
    
    def _evaluate_results(self, refined: List[Dict], all_products: List[Dict]) -> Dict:
        """Decide match status based on refined results."""
        if len(refined) == 1:
            return {
                "status": "best_match",
                "product": refined[0],
                "products": refined
            }
        
        if len(refined) > 1:
            return {
                "status": "multiple_matches",
                "product": None,
                "products": refined
            }
        
        # No matches (shouldn't happen with adaptive matching)
        return {
            "status": "multiple_matches",
            "product": None,
            "products": all_products
        }