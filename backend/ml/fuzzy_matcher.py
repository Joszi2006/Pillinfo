"""
Fuzzy Matcher - RapidFuzz matching only
Single Responsibility: Fuzzy string matching and correction
"""
from rapidfuzz import process, fuzz
from typing import Dict, List, Optional
from backend.core.config import Settings
from backend.util import log_mismatch

class FuzzyMatcher:
    """
    Handles all fuzzy string matching operations.
    Does NOT handle cache management - that's CacheService's job.
    """
    
    def __init__(
        self, 
        threshold: int = 85,
        scorer = fuzz.WRatio
    ):
        """
        Initialize fuzzy matcher.
        
        Args:
            threshold: Minimum similarity score (0-100)
            scorer: RapidFuzz scoring function
        """
        self.threshold = threshold
        self.scorer = scorer
        self.cache = None  # Will be injected by CacheService
    
    def set_cache(self, cache_dict: Dict[str, List[str]]):
        """
        Inject cache for matching operations.
        Called by CacheService to provide drug names.
        """
        self.cache = cache_dict
    
    def correct_drug_name(self, drug_name: str) -> Dict:
        """
        Correct drug name spelling using fuzzy matching.
        
        Args:
            drug_name: Drug name to correct
        
        Returns:
            {
                "original": str,
                "corrected": str,
                "confidence": int,
                "matched": bool
            }
        """
        if not self.cache:
            return {
                "original": drug_name,
                "corrected": drug_name,
                "confidence": 0,
                "matched": False,
                "note": "No cache available for matching"
            }
        
        # Try exact match first (case-insensitive)
        for cached_drug in self.cache.keys():
            if cached_drug.lower() == drug_name.lower():
                return {
                    "original": drug_name,
                    "corrected": cached_drug,
                    "confidence": 100,
                    "matched": True
                }
        
        # Fuzzy match
        best_match = process.extractOne(
            drug_name,
            self.cache.keys(),
            scorer=self.scorer,
            score_cutoff=self.threshold
        )
        
        if best_match:
            corrected_name = best_match[0]
            confidence = best_match[1]
            
            # Log the correction for improvement
            log_mismatch(drug_name, corrected_name, confidence, "fuzzy_correction")
            
            return {
                "original": drug_name,
                "corrected": corrected_name,
                "confidence": confidence,
                "matched": True
            }
        
        # No match found
        return {
            "original": drug_name,
            "corrected": drug_name,
            "confidence": 0,
            "matched": False
        }
    
    def find_in_cache(self, drug_name: str) -> Dict:
        """
        Find drug in cache using fuzzy matching.
        Similar to correct_drug_name but specifically for cache lookup.
        
        Args:
            drug_name: Drug name to find
        
        Returns:
            Match result dictionary
        """
        return self.correct_drug_name(drug_name)
    
    def match_product(self, query: str, products: List[str]) -> Optional[str]:
        """
        Match a query against a list of product names.
        Used for refining product results.
        
        Args:
            query: Search query
            products: List of product names to match against
        
        Returns:
            Best matching product name or None
        """
        if not products:
            return None
        
        best_match = process.extractOne(
            query,
            products,
            scorer=self.scorer,
            score_cutoff=70  # Lower threshold for product matching
        )
        
        if best_match:
            return best_match[0]
        
        return None
    
    def get_top_matches(
        self, 
        query: str, 
        limit: int = 5
    ) -> List[Dict]:
        """
        Get top N matches for a query.
        Useful for suggesting alternatives.
        
        Args:
            query: Query string
            limit: Number of results to return
        
        Returns:
            List of match dictionaries sorted by confidence
        """
        if not self.cache:
            return []
        
        matches = process.extract(
            query,
            self.cache.keys(),
            scorer=self.scorer,
            limit=limit
        )
        
        return [
            {
                "name": match[0],
                "confidence": match[1]
            }
            for match in matches
        ]
    
    def batch_correct(self, drug_names: List[str]) -> List[Dict]:
        """
        Correct multiple drug names efficiently.
        
        Args:
            drug_names: List of drug names to correct
        
        Returns:
            List of correction results
        """
        return [self.correct_drug_name(name) for name in drug_names]
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings.
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score (0-100)
        """
        return self.scorer(str1, str2)