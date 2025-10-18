"""
Text Processor Service - SHARED by both text and image streams (FIXED VERSION)
Single Responsibility: Process text through NER + Fuzzy matching + Data transformation
"""
from typing import Dict, Optional, List
from backend.ml.ner_extractor import NERExtractor
from backend.ml.fuzzy_matcher import FuzzyMatcher
import re

# Configuration constants
MIN_WEIGHT_KG = 1.0  # Minimum reasonable weight in kg
MAX_WEIGHT_KG = 500.0  # Maximum reasonable weight in kg
MIN_AGE_YEARS = 0  # Minimum age in years
MAX_AGE_YEARS = 120  # Maximum age in years
LBS_TO_KG_CONVERSION = 0.453592  # Conversion factor

class TextProcessor:
    """
    Processes text through NER and fuzzy matching.
    
    Responsibilities:
    1. Extract entities (via NER)
    2. Correct typos (via fuzzy matching)
    3. Transform/convert extracted data to usable formats
    """
    
    def __init__(self):
        self.ner_extractor = NERExtractor()
        self.fuzzy_matcher = FuzzyMatcher()
    
    def process_text(self, text: str, use_ner: bool = True) -> Dict:
        """
        Process text to extract and transform drug information and patient data.
        
        Args:
            text: Input text from user or OCR
            use_ner: Whether to use NER extraction
            
        Returns:
            Dictionary with extracted and transformed data
        """
        if not use_ner:
            return {
                "brand_name": text.strip(),
                "dosage": None,
                "dosage_numeric": None,
                "route": None,
                "form": None,
                "weight_kg": None,
                "age_years": None,
                "entities": None,
                "correction": None,
                "all_drugs": []
            }
        
        # Step 1: Extract all entities using NER (returns raw strings)
        entities = self.ner_extractor.extract(text)
        
        # Step 2: Handle drug extraction and correction
        drugs = entities.get("drugs", [])
        
        if not drugs:
            return {
                "brand_name": None,
                "dosage": None,
                "dosage_numeric": None,
                "route": None,
                "form": None,
                "weight_kg": None,
                "age_years": None,
                "entities": entities,
                "correction": None,
                "all_drugs": [],
                "error": "No drug names detected"
            }
        
        # Process the first drug (primary)
        extracted_drug = drugs[0]
        
        # Always run through fuzzy matcher to correct typos
        correction = self.fuzzy_matcher.correct_drug_name(extracted_drug)
        final_drug_name = correction["corrected"] if correction["matched"] else extracted_drug
    
        
        # Step 3: Extract and transform other entities
        dosages = entities.get("dosages", [])
        weights = entities.get("weights", [])
        ages = entities.get("ages", [])
        routes = entities.get("routes", [])
        forms = entities.get("forms", [])
        
        dosage_str = dosages[0] if dosages else None
        weight_str = weights[0] if weights else None
        age_str = ages[0] if ages else None
        route = routes[0] if routes else None
        form = forms[0] if forms else None
        
        # Convert to numbers with validation
        dosage_numeric = self._extract_dosage_numeric(dosage_str)
        weight_kg = self._convert_weight_to_kg(weight_str)
        age_years = self._convert_age_to_years(age_str)
        
        # Step 4: Return all processed data
        return {
            "brand_name": final_drug_name,
            "dosage": dosage_str,
            "dosage_numeric": dosage_numeric,
            "route": route,
            "form": form,
            "weight_kg": weight_kg,
            "age_years": age_years,
            "entities": entities,
            "correction": correction,
            "all_drugs": drugs,
            "original_text": text
        }
    
    def _extract_dosage_numeric(self, dosage_str: str) -> Optional[float]:
        """
        Extract numeric value from dosage string (e.g., '200mg' -> 200.0)
        
        Returns None if no valid number found or if value is unreasonable.
        """
        if not dosage_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)', dosage_str)
        if match:
            value = float(match.group(1))
            # Validate reasonable dosage range (0.01mg to 10000mg)
            if 0.01 <= value <= 10000:
                return value
        
        return None
    
    def _convert_weight_to_kg(self, weight_str: str) -> Optional[float]:
        """
        Convert weight string to kg (e.g., '52kg' -> 52.0, '120lbs' -> 54.4)
        
        Returns None if conversion fails or value is outside reasonable range.
        """
        if not weight_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)\s*([a-z]+)', weight_str, re.IGNORECASE)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2).lower()
        
        # Convert lbs to kg if needed
        if 'lb' in unit or 'pound' in unit:
            value = value * LBS_TO_KG_CONVERSION
        
        # Validate reasonable weight range
        if MIN_WEIGHT_KG <= value <= MAX_WEIGHT_KG:
            return round(value, 2)  # Round to 2 decimal places
        
        return None
    
    def _convert_age_to_years(self, age_str: str) -> Optional[int]:
        """
        Convert age string to years (e.g., '14 years old' -> 14)
        
        Returns None if conversion fails or value is outside reasonable range.
        """
        if not age_str:
            return None
        
        match = re.search(r'(\d+)', age_str)
        if not match:
            return None
        
        age = int(match.group(1))
        
        # Validate reasonable age range
        if MIN_AGE_YEARS <= age <= MAX_AGE_YEARS:
            return age
        
        return None
    
    def inject_cache(self, cache_dict: Dict):
        """Inject cache into fuzzy matcher for typo correction."""
        self.fuzzy_matcher.set_cache(cache_dict)
    
    