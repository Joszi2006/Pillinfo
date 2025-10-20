"""
Cache Service - Cache management only
Single Responsibility: Handle all cache operations
"""
from typing import List, Dict, Optional
from backend.utilities.util import load_cached_labels, save_cached_labels, get_cache_stats
from backend.services.rxnorm_service import RxNormService
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
        
        Args:
            brand_name: Brand name to look up
        
        Returns:
            List of products or None if not cached
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
        
        Args:
            brand_name: Brand name
            products: List of product names
        
        Returns:
            True if successful
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
    
    async def seed_common_drugs(self) -> Dict:
        """
        Seed cache with commonly prescribed drugs.
        
        Returns:
            Statistics about seeding operation
        """
        common_drugs = [
            # Cardiovascular
            "Lipitor", "Crestor", "Plavix", "Lisinopril", "Atorvastatin",
            "Metoprolol", "Amlodipine", "Losartan", "Warfarin",
            
            # Diabetes
            "Metformin", "Lantus", "Humalog", "Januvia", "Glipizide",
            
            # Pain/Inflammation
            "Advil", "Tylenol", "Aspirin", "Ibuprofen", "Naproxen",
            "Celebrex", "Tramadol",
            
            # Respiratory
            "Ventolin", "Advair", "Singulair", "Symbicort", "Albuterol",
            
            # GI
            "Nexium", "Prilosec", "Zantac", "Omeprazole",
            
            # Mental Health
            "Zoloft", "Prozac", "Lexapro", "Xanax", "Abilify",
            
            # Antibiotics
            "Amoxicillin", "Azithromycin", "Cipro", "Doxycycline"
        ]
        
        cache = self._load_cache()
        new_count = 0
        failed_count = 0
        
        for drug in common_drugs:
            if drug not in cache:
                products = await self.rxnorm_service.fetch_products(drug)
                if products:
                    cache[drug] = products
                    new_count += 1
                    logger.info(f"Seeded: {drug}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to seed: {drug}")
        
        # Save updated cache
        self._cache = cache
        save_cached_labels(cache)
        
        return {
            "message": "Cache seeding completed",
            "new_brands_added": new_count,
            "failed_brands": failed_count,
            "total_brands": len(cache),
            "total_products": sum(len(v) for v in cache.values())
        }
    
    def get_cache_dict(self) -> Dict[str, List[str]]:
        """
        Get the entire cache dictionary.
        Used by FuzzyMatcher for matching operations.
        """
        return self._load_cache()