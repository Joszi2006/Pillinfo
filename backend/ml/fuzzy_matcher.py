"""
Fuzzy Matcher - Drug Name Typo Correction

Corrects misspellings in drug names using fuzzy string matching.
"""
from rapidfuzz import process, fuzz
from pathlib import Path
from typing import Optional, List, Dict
import json

# Configuration constants
DEFAULT_SIMILARITY_THRESHOLD = 70
MIN_SIMILARITY_SCORE = 0.0


class FuzzyMatcher:
    """Corrects typos in drug names"""
    
    def __init__(self, threshold: int = DEFAULT_SIMILARITY_THRESHOLD):
        """
        Initialize fuzzy matcher.
        
        Args:
            threshold: Minimum similarity score (0-100)
        """
        self.threshold = threshold
        self.known_drugs = self._load_known_drugs()
    
    def _load_known_drugs(self) -> set:
        """Load all known drug names from common_drugs.json."""
        try:
            drugs_file = Path(__file__).parent.parent.parent / "data" / "common_drugs.json"
            with open(drugs_file, 'r') as f:
                data = json.load(f)
            
            all_names = set()
            for generic, info in data.items():
                all_names.add(generic.lower())
                for brand in info["brands"]:
                    all_names.add(brand.lower())
            
            # print(f"Fuzzy matcher loaded {len(all_names)} drug names")
            return all_names
            
        except Exception as e:
            print(f"Could not load common_drugs.json: {e}")
            return set()
    
    def correct(self, drug_name: str) -> Optional[str]:
        """
        Correct typos in drug name using fuzzy matching.
        Returns corrected name or None if no match found.
        """
        if not drug_name or not drug_name.strip():
            return None
        
        cleaned = drug_name.strip().lower()
        
        # Exact match (fastest path)
        if cleaned in self.known_drugs:
            return drug_name.strip()
        
        # Fuzzy match
        result = process.extractOne(
            cleaned,
            list(self.known_drugs),
            scorer=fuzz.WRatio,
            score_cutoff=self.threshold
        )
        
        if result:
            corrected = result[0]
            confidence = result[1]
            # print(f"Corrected: '{drug_name}' → '{corrected}' ({confidence:.0f}%)")
            return corrected
        
        return None
    
    def batch_correct(self, drug_names: List[str]) -> List[Dict[str, any]]:
        """
        Correct multiple drug names efficiently.
        Returns list of correction results in same order as input.
        """
        if not drug_names:
            return []
        
        results = []
        for drug_name in drug_names:
            corrected = self.correct(drug_name)
            results.append({
                "original": drug_name,
                "corrected": corrected if corrected else drug_name,
                "matched": corrected is not None
            })
        
        return results
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings (0-100).
        Useful for future fuzzy operations.
        """
        if not str1 or not str2:
            return MIN_SIMILARITY_SCORE
        return float(fuzz.WRatio(str1.strip(), str2.strip()))