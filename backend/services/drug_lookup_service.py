"""
Drug Lookup Service - Coordinates drug lookup
"""
from typing import List, Optional, Dict
from services.rxnorm_service import RxNormService
from api.dependencies import get_drug_database
from rapidfuzz import fuzz


class DrugLookupService:
    """Coordinates drug lookup from database or API."""
    
    def __init__(self):
        self.rxnorm_service = RxNormService()
        self.database = get_drug_database()
    
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
        
        products = await self._fetch_products(brand_name)
        
        if not products:
            return {
                "status": "not_found",
                "product": None,
                "products": []
            }
        
        if len(products) == 1:
            return {
                "status": "best_match",
                "product": products[0],
                "products": products
            }
        
        refined = self.refine_products(
            products, brand_name, dosage, route, form
        )
        
        return self._evaluate_results(refined, products)
    
    async def _fetch_products(self, brand_name: str) -> List:
        """Get products from database or API."""
        cached = self.database.get_products_by_brand(brand_name)
        if cached:
            return [
                {
                    "rxcui": p["rxcui"],
                    "brand_name": p["brand_name"],
                    "name": p.get("product_name") or p.get("name")
                }
                for p in cached
            ]
        
        result = await self.rxnorm_service.get_drug_details(brand_name)
        
        if result and result.get("products"):
            for product in result["products"]:
                self.database.save_product(
                    rxcui=product["rxcui"],
                    brand_name=brand_name,
                    product_name=product["name"]
                )
            return result["products"]
        
        return []
    
    def refine_products(
        self,
        products: List[Dict],
        brand_name: Optional[str],
        dosage: Optional[str] = None,
        route: Optional[str] = None,
        form: Optional[str] = None
    ) -> List[Dict]:
        """Filter products using WRatio fuzzy matching."""
        if not products or not any([dosage, route, form]):
            return products
        
        query_parts = [brand_name]
        if dosage:
            query_parts.append(dosage)
        if form:
            query_parts.append(form)
        if route:
            query_parts.append(route)
        
        query = " ".join(query_parts).lower()
        
        scored = []
        for product in products:
            name = product.get("name") or product.get("product_name", "")
            score = fuzz.WRatio(query, name.lower())
            scored.append((product, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top_score = scored[0][1]
        
        # If top score is poor, return all products
        if top_score == 100:
            return [scored[0][0]]
        
        if top_score < 60:
            return products
        
        # Return products within 10 points of top score
        return [p for p, s in scored if s >= top_score - 10]
    
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
        
        return {
            "status": "multiple_matches",
            "product": None,
            "products": all_products
        }