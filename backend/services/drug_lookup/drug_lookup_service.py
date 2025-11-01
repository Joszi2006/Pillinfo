"""
Drug Lookup Service 
"""
from typing import List, Tuple, Optional, Dict
from backend.services.drug_lookup.rxnorm_service import RxNormService
from backend.services.cache_service import CacheService
from backend.services.drug_lookup.openfda_service import OpenFDAService


class DrugLookupService:
    """
    Looks up drug products from cache or RxNorm API.
    """
    
    def __init__(
        self,
        rxnorm_service: Optional[RxNormService] = None,
        cache_service: Optional[CacheService] = None,
        openfda_service: Optional[OpenFDAService] = None
    ):
        """Initialize with dependency injection support."""
        self.rxnorm_service = rxnorm_service or RxNormService()
        self.cache_service = cache_service or CacheService()
        self.openfda_service = openfda_service or OpenFDAService()
    
    async def lookup_drug(self, brand_name: str) -> Tuple[List[str], str, Optional[str]]:
        """
        Look up drug products by brand name.
        
        Returns:
            Tuple of (product_list, source, generic_name)
        """
        if not brand_name or not brand_name.strip():
            return [], "invalid_input", None
        
        brand_name = brand_name.strip()
        
        # CHECK CACHE
        cached = self.cache_service.get(brand_name)
        if cached:
            
            #  HANDLE NEW DICT FORMAT
            if isinstance(cached, dict) and "products" in cached:
                return (
                    cached["products"],  # ← Extract the products LIST
                    f"cache:{brand_name}",
                    cached.get("generic_name")
                )
            elif isinstance(cached, list):
                # Old cache format
                return cached, f"cache:{brand_name}", None
        
        # FETCH FROM API
        result = await self.rxnorm_service.get_drug_details(brand_name)
        
        if result and result.get("products"):
            # Cache the full dict
            self.cache_service.save(brand_name, result)
            
            return (
                result["products"],  # Extract the products LIST
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
    
        if not products or not (dosage or route or form):
            return products
        
        search_terms = []
        if dosage:
            search_terms.append(dosage.lower().strip())
        if route:
            search_terms.append(route.lower().strip())
        if form:
            search_terms.append(form.lower().strip())
        
        product_names = []
        for p in products:
            if isinstance(p, dict):
                product_names.append(p.get("name", "").lower())
            else:
                product_names.append(str(p).lower())
        
        exact_matches = [
            products[i] for i, p_lower in enumerate(product_names)
            if all(term in p_lower for term in search_terms)
        ]
        
        if exact_matches:
            return exact_matches
        
        partial_matches = [
            products[i] for i, p_lower in enumerate(product_names)
            if any(term in p_lower for term in search_terms)
        ]
        
        return partial_matches if partial_matches else []
        
    def evaluate_product_matches(
        self,
        products: List,
        refined: List,
        user_was_specific: bool
    ) -> Dict:
        """
        Evaluate product matching results and determine match quality.
        Returns STRUCTURED DATA only (no user-facing messages).
        
        Args:
            products: Full list of products found
            refined: Filtered products based on user criteria
            user_was_specific: Whether user provided dosage/route/form
        
        Returns:
            {
                "match_type": "exact" | "multiple" | "none" | "vague",
                "best_match": product or None,
                "sample_products": List of 3-5 products to show,
                "match_count": int
            }
        """
        
        # Case 1: User was specific AND we found matches
        if user_was_specific and refined:
            
            if len(refined) == 1:
                # PERFECT - Exactly one match
                return {
                    "match_type": "exact",
                    "best_match": refined[0],
                    "sample_products": refined,
                    "match_count": 1
                }
            
            else:
                # MULTIPLE matches - still ambiguous
                return {
                    "match_type": "multiple",
                    "best_match": None,
                    "sample_products": refined[:5],  # Show up to 5
                    "match_count": len(refined)
                }
        
        # Case 2: User was specific but NO matches found
        elif user_was_specific and not refined:
            return {
                "match_type": "none",
                "best_match": None,
                "sample_products": products[:3],  # Show 3 examples of what exists
                "match_count": 0
            }
        
        # Case 3: User was NOT specific (just "Advil")
        else:
            return {
                "match_type": "vague",
                "best_match": None,
                "sample_products": products[:3],  # Show 3 examples
                "match_count": len(products)
            }