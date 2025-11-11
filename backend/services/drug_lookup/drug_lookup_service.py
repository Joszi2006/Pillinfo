"""
Drug Lookup Service
"""
from typing import List, Tuple, Optional, Dict
from backend.services.drug_lookup.rxnorm_service import RxNormService
from backend.services.cache_service import CacheService
from backend.services.drug_lookup.product_matcher import ProductMatcher


class DrugLookupService:
    """Coordinates drug lookup from cache or API."""
    
    def __init__(
        self,
        rxnorm_service: Optional[RxNormService] = None,
        cache_service: Optional[CacheService] = None,
        product_matcher: Optional[ProductMatcher] = None
    ):
        self.rxnorm_service = rxnorm_service or RxNormService()
        self.cache_service = cache_service or CacheService()
        self.product_matcher = product_matcher or ProductMatcher()
    
    async def lookup_drug(self, brand_name: str) -> Tuple[List[Dict], str, Optional[str]]:
        """
        Look up drug products by brand name.
        
        Returns:
            Tuple of (products, source, generic_name)
        """
        if not brand_name or not brand_name.strip():
            return [], "invalid_input", None
        
        brand_name = brand_name.strip()
        
        cached = self.cache_service.get(brand_name)
        if cached:
            if isinstance(cached, dict) and "products" in cached:
                return (
                    cached["products"],
                    f"cache:{brand_name}",
                    cached.get("generic_name")
                )
            elif isinstance(cached, list):
                return cached, f"cache:{brand_name}", None
        
        result = await self.rxnorm_service.get_drug_details(brand_name)
        
        if result and result.get("products"):
            self.cache_service.save(brand_name, result)
            return (
                result["products"],
                "api",
                result.get("generic_name")
            )
        
        return [], "not_found", None
    
    def refine_products(
        self,
        products: List[Dict],
        dosage: Optional[str] = None,
        route: Optional[str] = None,
        form: Optional[str] = None
    ) -> List[Dict]:
        """Filter products using ProductMatcher."""
        return self.product_matcher.refine_products(products, dosage, route, form)
    
    def evaluate_product_matches(
        self,
        products: List[Dict],
        refined: List[Dict],
        user_was_specific: bool
    ) -> Dict:
        """Evaluate matches using ProductMatcher."""
        return self.product_matcher.evaluate_matches(products, refined, user_was_specific)