"""
Product Matcher - Handles product filtering and evaluation
"""
from typing import List, Optional, Dict
from difflib import SequenceMatcher


class ProductMatcher:
    """Match and evaluate products with fuzzy matching."""
    
    FUZZY_THRESHOLD = 0.75
    
    def refine_products(
        self,
        products: List[Dict],
        dosage: Optional[str] = None,
        route: Optional[str] = None,
        form: Optional[str] = None
    ) -> List[Dict]:
        """Filter products using fuzzy matching."""
        
        if not products or not (dosage or route or form):
            return products
        
        search_query = self._build_search_query(dosage, route, form)
        
        scored_products = []
        for product in products:
            product_name = self._get_product_name(product)
            score = self._fuzzy_score(search_query, product_name)
            
            if score >= self.FUZZY_THRESHOLD:
                scored_products.append((score, product))
        
        scored_products.sort(reverse=True, key=lambda x: x[0])
        return [product for score, product in scored_products]
    
    def evaluate_matches(
        self,
        products: List[Dict],
        refined: List[Dict],
        user_was_specific: bool
    ) -> Dict:
        """Evaluate quality of product matches."""
        
        if user_was_specific and refined:
            if len(refined) == 1:
                return {
                    "match_type": "exact",
                    "best_match": refined[0],
                    "sample_products": refined,
                    "match_count": 1
                }
            else:
                return {
                    "match_type": "multiple",
                    "best_match": None,
                    "sample_products": refined[:3],
                    "match_count": len(refined)
                }
        
        elif user_was_specific and not refined:
            return {
                "match_type": "none",
                "best_match": None,
                "sample_products": products[:3],
                "match_count": 0
            }
        
        else:
            return {
                "match_type": "vague",
                "best_match": None,
                "sample_products": products[:3],
                "match_count": len(products)
            }
    
    def _build_search_query(
        self,
        dosage: Optional[str],
        route: Optional[str],
        form: Optional[str]
    ) -> str:
        """Build search query from user terms."""
        parts = []
        if dosage:
            parts.append(dosage.strip())
        if route:
            parts.append(route.strip())
        if form:
            parts.append(form.strip())
        return " ".join(parts).lower()
    
    def _fuzzy_score(self, search_text: str, product_name: str) -> float:
        """Calculate similarity between search and product name."""
        return SequenceMatcher(
            None,
            search_text.lower(),
            product_name.lower()
        ).ratio()
    
    def _get_product_name(self, product: Dict) -> str:
        """Extract product name safely."""
        if isinstance(product, dict):
            return product.get("name", "")
        return str(product)