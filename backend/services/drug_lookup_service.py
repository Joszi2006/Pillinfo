"""
Drug Lookup Service - SIMPLIFIED
Single Responsibility: Query cache or RxNorm API for drug products
"""
from typing import List, Tuple, Optional, Dict
from backend.services.rxnorm_service import RxNormService
from backend.services.cache_service import CacheService


class DrugLookupService:
    """
    Looks up drug products from cache or RxNorm API.
    Assumes input is already cleaned/corrected by TextProcessor.
    """
    
    def __init__(
        self,
        rxnorm_service: Optional[RxNormService] = None,
        cache_service: Optional[CacheService] = None
    ):
        """Initialize with dependency injection support."""
        self.rxnorm_service = rxnorm_service or RxNormService()
        self.cache_service = cache_service or CacheService()
    
    async def lookup_drug(self, brand_name: str) -> Tuple[List[Dict], str]:
        """
        Look up drug products by brand name.
        
        Assumes brand_name is already cleaned/corrected by TextProcessor.
        
        Args:
            brand_name: Clean drug brand name (e.g., "Tylenol")
        
        Returns:
            Tuple of (list of products, source string)
        """
        # Validate input
        if not brand_name or not brand_name.strip():
            return [], "invalid_input"
        
        brand_name = brand_name.strip()
        
        # Step 1: Check cache (exact match)
        cached_products = self.cache_service.get(brand_name)
        if cached_products:
            return cached_products, f"cache:{brand_name}"
        
        # Step 2: Not in cache - fetch from RxNorm API
        products = await self.rxnorm_service.fetch_products(brand_name)
        
        if products:
            # Cache for future lookups
            self.cache_service.save(brand_name, products)
            return products, "api"
        
        return [], "not_found"
    
    def refine_products(
        self,
        products: List[Dict],
        dosage: Optional[str] = None,
        route: Optional[str] = None,
        form: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter products based on dosage, route, and form.
        
        Args:
            products: List of product dictionaries
            dosage: Dosage string (e.g., "200mg")
            route: Administration route (e.g., "oral")
            form: Drug form (e.g., "tablet")
        
        Returns:
            Filtered list of products (empty if no matches)
        """
        if not products or not (dosage or route or form):
            return products
        
        # Build search terms
        search_terms = []
        if dosage:
            search_terms.append(dosage.lower().strip())
        if route:
            search_terms.append(route.lower().strip())
        if form:
            search_terms.append(form.lower().strip())
        
        # Extract and lowercase product names once
        product_names = []
        for p in products:
            if isinstance(p, dict):
                product_names.append(p.get("name", "").lower())
            else:
                product_names.append(str(p).lower())
        
        # Exact matches (all terms present)
        exact_matches = [
            products[i] for i, p_lower in enumerate(product_names)
            if all(term in p_lower for term in search_terms)
        ]
        
        if exact_matches:
            return exact_matches
        
        # Partial matches (at least one term)
        partial_matches = [
            products[i] for i, p_lower in enumerate(product_names)
            if any(term in p_lower for term in search_terms)
        ]
        
        return partial_matches if partial_matches else []