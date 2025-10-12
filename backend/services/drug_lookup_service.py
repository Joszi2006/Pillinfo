"""
Drug Lookup Service - ONLY looks up drugs
Single Responsibility: Query cache or RxNorm API for drug products
"""
from typing import Dict, List, Tuple
from backend.services.rxnorm_service import RxNormService
from backend.services.cache_service import CacheService
from backend.ml.fuzzy_matcher import FuzzyMatcher

class DrugLookupService:
    """
    Looks up drug products from cache or RxNorm API.
    Does NOT do text processing - that's TextProcessor's job!
    
    Single Responsibility: Find drug products given a drug name
    """
    
    def __init__(self):
        self.rxnorm_service = RxNormService()
        self.cache_service = CacheService()
        self.fuzzy_matcher = FuzzyMatcher()
        
        # Inject cache into fuzzy matcher
        self.fuzzy_matcher.set_cache(self.cache_service.get_cache_dict())
    
    async def lookup_drug(self, brand_name: str) -> Tuple[List[str], str]:
        """
        Look up drug products by brand name.
        Checks cache first, then queries RxNorm API.
        
        Args:
            brand_name: Drug brand name (already processed/corrected)
        
        Returns:
            Tuple of (products list, source string)
        """
        # Step 1: Check cache (exact match)
        cached_products = self.cache_service.get(brand_name)
        if cached_products:
            return cached_products, f"cache_exact:{brand_name}"
        
        # Step 2: Try fuzzy match on cache
        fuzzy_result = self.fuzzy_matcher.find_in_cache(brand_name)
        if fuzzy_result["matched"]:
            matched_brand = fuzzy_result["corrected"]
            products = self.cache_service.get(matched_brand)
            if products:
                return products, f"cache_fuzzy:{matched_brand}:{fuzzy_result['confidence']}"
        
        # Step 3: Fetch from RxNorm API
        products = await self.rxnorm_service.fetch_products(brand_name)
        
        if products:
            # Cache the result for future
            self.cache_service.save(brand_name, products)
            return products, "api_fetched"
        
        return [], "not_found"
    
    def refine_products(
        self,
        products: List[str],
        dosage: str = None,
        route: str = None,
        form: str = None
    ) -> List[str]:
        """
        Filter products based on dosage, route, and form.
        
        Args:
            products: List of all products
            dosage: Desired dosage (e.g., "20mg")
            route: Desired route (e.g., "oral")
            form: Desired form (e.g., "tablet")
        
        Returns:
            Filtered list of products
        """
        if not (dosage or route or form):
            return products
        
        search_terms = []
        if dosage:
            search_terms.append(dosage.lower())
        if route:
            search_terms.append(route.lower())
        if form:
            search_terms.append(form.lower())
        
        # Exact substring matches
        matches = [
            p for p in products
            if all(term in p.lower() for term in search_terms)
        ]
        
        # Fuzzy fallback
        if not matches and search_terms:
            query = " ".join(search_terms)
            fuzzy_match = self.fuzzy_matcher.match_product(query, products)
            if fuzzy_match:
                matches = [fuzzy_match]
        
        return matches if matches else products