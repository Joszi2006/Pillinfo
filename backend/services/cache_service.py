"""
Cache Service - Cache management only
"""
from typing import List, Dict, Optional
from backend.utilities.util import load_cached_labels, save_cached_labels, get_cache_stats
from backend.services.drug_lookup.rxnorm_service import RxNormService
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """
    Manages drug product cache.
    Handles loading, saving, and seeding operations.
    """
    
    def __init__(self):
        self._cache = None
        self.rxnorm_service = RxNormService()
    
    def _load_cache(self) -> Dict[str, List[str]]:
        """Lazy load cache."""
        if self._cache is None:
            self._cache = load_cached_labels()
        return self._cache
    
    def get(self, brand_name: str) -> Optional[List[str]]:
        """
        Get products for a brand name from cache.
        """
        cache = self._load_cache()
        
        # Exact match (case-insensitive)
        for cached_brand in cache.keys():
            if cached_brand.lower() == brand_name.lower():
                return cache[cached_brand]
        
        return None
    
    def save(self, brand_name: str, products: List[str]) -> bool:
        """
        Save products to cache.
        """
        cache = self._load_cache()
        cache[brand_name] = products
        self._cache = cache
        
        success = save_cached_labels(cache)
        
        if success:
            logger.info(f"Cached {len(products)} products for '{brand_name}'")
        
        return success
    
    def get_all_brands(self) -> List[str]:
        """Get list of all cached brand names."""
        cache = self._load_cache()
        return list(cache.keys())
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return get_cache_stats()
    
    def clear(self) -> bool:
        """Clear the entire cache."""
        self._cache = {}
        return save_cached_labels({})
    
    def get_cache_dict(self) -> Dict[str, List[str]]:
        """
        Get the entire cache dictionary.
        Used by FuzzyMatcher for matching operations.
        """
        return self._load_cache()