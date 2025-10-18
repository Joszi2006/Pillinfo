"""
Fuzzy Matcher - RapidFuzz matching only (CLEAN VERSION)
Single Responsibility: Fuzzy string matching and correction
"""
from rapidfuzz import process, fuzz
from typing import Dict, List, Optional, Callable

# Configuration constants
DEFAULT_THRESHOLD = 70
MIN_THRESHOLD = 0
MAX_THRESHOLD = 100

# Optional logging - won't crash if unavailable
try:
    from backend.util import log_mismatch
    HAS_LOGGING = True
except ImportError:
    HAS_LOGGING = False
    log_mismatch = None


class FuzzyMatcher:
    """
    Handles all fuzzy string matching operations.
    Does NOT handle cache management - that's CacheService's job.
    """
    
    def __init__(
        self, 
        threshold: int = DEFAULT_THRESHOLD,
        scorer: Callable[[str, str], float] = fuzz.WRatio,
        log_callback: Optional[Callable] = None
    ):
        """
        Initialize fuzzy matcher.
        
        Args:
            threshold: Minimum similarity score (0-100)
            scorer: RapidFuzz scoring function
            log_callback: Optional callback for logging corrections
        
        Raises:
            ValueError: If threshold is outside valid range
        """
        if not MIN_THRESHOLD <= threshold <= MAX_THRESHOLD:
            raise ValueError(
                f"Threshold must be between {MIN_THRESHOLD} and {MAX_THRESHOLD}, got {threshold}"
            )
        
        self.threshold = threshold
        self.scorer = scorer
        self.cache: Optional[List[str]] = None
        self.log_callback = log_callback or self._default_logger
    
    def _default_logger(self, *args, **kwargs):
        """Default no-op logger."""
        pass
    
    def set_cache(self, cache_dict: Dict[str, List[str]]):
        """
        Inject cache for matching operations.
        
        Args:
            cache_dict: Dictionary where keys are drug names
                       (values are ignored - only keys are used for matching)
        """
        self.cache = list(cache_dict.keys()) if cache_dict else []
    
    def correct_drug_name(self, drug_name: str) -> Dict:
        """
        Correct drug name spelling using fuzzy matching.
        
        Case Handling:
        - Matching is case-insensitive
        - Returns the cached drug name's case (standardized spelling)
        - Example: "tylenol" -> "Tylenol" (uses cache's capitalization)
        
        Args:
            drug_name: Drug name to correct (any case)
        
        Returns:
            {
                "original": str (input as-is),
                "corrected": str (standardized from cache),
                "confidence": int (0-100),
                "matched": bool
            }
        """
        # Validate input
        if not drug_name or not drug_name.strip():
            return {
                "original": drug_name,
                "corrected": "",
                "confidence": 0,
                "matched": False
            }
        
        drug_name_clean = drug_name.strip()
        
        # Check if cache is available
        if not self.cache:
            return {
                "original": drug_name,
                "corrected": drug_name,
                "confidence": 0,
                "matched": False
            }
        
        # Try exact match first (case-insensitive) - fastest path
        for cached_drug in self.cache:
            if cached_drug.lower() == drug_name_clean.lower():
                return {
                    "original": drug_name,
                    "corrected": cached_drug,
                    "confidence": 100,
                    "matched": True
                }
        
        # Fuzzy match
        best_match = process.extractOne(
            drug_name_clean,
            self.cache,
            scorer=self.scorer,
            score_cutoff=self.threshold
        )
        
        if best_match:
            corrected_name = best_match[0]
            confidence = best_match[1]
            
            # Log the correction (safe - won't crash if logging fails)
            self._safe_log(drug_name_clean, corrected_name, confidence, "fuzzy_correction")
            
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
    
    def _safe_log(self, original: str, corrected: str, confidence: float, log_type: str):
        """
        Safely log corrections without crashing if logging fails.
        Only place we need try-catch - external dependency.
        """
        try:
            if HAS_LOGGING and log_mismatch:
                log_mismatch(original, corrected, confidence, log_type)
            else:
                self.log_callback(original, corrected, confidence, log_type)
        except Exception:
            # Silently fail - logging should never crash the application
            pass
    
    def match_product(
        self, 
        query: str, 
        products: List[str],
        threshold: Optional[int] = None
    ) -> Optional[str]:
        """
        Match a query against a list of product names.
        
        Args:
            query: Search query
            products: List of product names to match against
            threshold: Custom threshold (defaults to self.threshold)
        
        Returns:
            Best matching product name or None
        """
        if not products or not query or not query.strip():
            return None
        
        # Use instance threshold unless overridden
        cutoff = threshold if threshold is not None else self.threshold
        
        best_match = process.extractOne(
            query.strip(),
            products,
            scorer=self.scorer,
            score_cutoff=cutoff
        )
        
        return best_match[0] if best_match else None
    
    def get_top_matches(
        self, 
        query: str, 
        limit: int = 5
    ) -> List[Dict]:
        """
        Get top N matches for a query.
        
        Args:
            query: Query string
            limit: Number of results to return
        
        Returns:
            List of match dictionaries sorted by confidence (highest first)
        """
        if not self.cache or not query or not query.strip():
            return []
        
        matches = process.extract(
            query.strip(),
            self.cache,
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
            List of correction results (same order as input)
        """
        if not drug_names:
            return []
        
        if not self.cache:
            return [{
                "original": name,
                "corrected": name,
                "confidence": 0,
                "matched": False
            } for name in drug_names]
        
        results = []
        for drug_name in drug_names:
            if not drug_name or not drug_name.strip():
                results.append({
                    "original": drug_name,
                    "corrected": "",
                    "confidence": 0,
                    "matched": False
                })
            else:
                # Reuse the main method for consistency
                results.append(self.correct_drug_name(drug_name))
        
        return results
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings.
        
        Args:
            str1: First string
            str2: Second string
        
        Returns:
            Similarity score (0-100), or 0 if either string is empty
        """
        if not str1 or not str2:
            return 0.0
        
        return float(self.scorer(str1.strip(), str2.strip()))