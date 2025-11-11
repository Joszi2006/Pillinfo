"""
Text Processor - Extract and normalize drug information
"""
from typing import Dict, Optional
from backend.ml.ner_extractor import NERExtractor
import re


class TextProcessor:
    """Extract and normalize drug information from text."""
    
    LBS_TO_KG = 0.453592
    
    def __init__(self, ner_extractor: Optional[NERExtractor] = None):
        self.ner_extractor = ner_extractor or NERExtractor()
    
    def process_text(self, text: str, use_ner: bool = True) -> Dict:
        """
        Extract drug information from text.
        
        Returns normalized data without validation.
        """
        if not text or not text.strip():
            return {"error": "Empty input"}
        
        if not use_ner:
            return {
                "brand_name": text.strip(),
                "dosage": None,
                "dosage_numeric": None,
                "route": None,
                "form": None,
                "weight_kg": None,
                "age_years": None
            }
        
        cleaned_text = self._clean_text(text)
        entities = self.ner_extractor.extract(cleaned_text)
        
        drugs = entities.get("drugs", [])
        if not drugs:
            return {"error": "No drug names detected"}
        
        dosages = entities.get("dosages", [])
        weights = entities.get("weights", [])
        ages = entities.get("ages", [])
        routes = entities.get("routes", [])
        forms = entities.get("forms", [])
        
        return {
            "brand_name": drugs[0],
            "dosage": self._normalize_dosage(dosages[0]) if dosages else None,
            "dosage_numeric": self._extract_numeric(dosages[0]) if dosages else None,
            "route": routes[0].lower().strip() if routes else None,
            "form": forms[0].lower().strip() if forms else None,
            "weight_kg": self._parse_weight(weights[0]) if weights else None,
            "age_years": self._parse_age(ages[0]) if ages else None
        }
    
    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace."""
        return " ".join(text.split()).strip()
    
    # def _normalize_dosage(self, dosage_str: str) -> Optional[str]:
    #     """Normalize dosage format."""
    #     if not dosage_str:
    #         return None
        
    #     match = re.search(r'(\d+\.?\d*)\s*([a-zA-Z/]+)', dosage_str, re.IGNORECASE)
    #     if not match:
    #         return None
        
    #     number = match.group(1)
    #     unit = match.group(2).lower()
    #     unit = re.sub(r'\s*/\s*', '/', unit)
        
    #     return f"{number} {unit}"
    
    def _extract_numeric(self, dosage_str: str) -> Optional[float]:
        """Extract numeric value from dosage."""
        if not dosage_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)', dosage_str)
        if match:
            return float(match.group(1))
        return None
    
    def _parse_weight(self, weight_str: str) -> Optional[float]:
        """Parse weight and convert to kg."""
        if not weight_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)\s*([a-z]+)', weight_str, re.IGNORECASE)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2).lower()
        
        if 'lb' in unit or 'pound' in unit:
            value = value * self.LBS_TO_KG
        
        return round(value, 2)
    
    def _parse_age(self, age_str: str) -> Optional[int]:
        """Extract age in years."""
        if not age_str:
            return None
        
        match = re.search(r'(\d+)', age_str)
        if match:
            return int(match.group(1))
        return None