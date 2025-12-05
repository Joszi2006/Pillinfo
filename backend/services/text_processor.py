"""
Text Processor - Extract and normalize drug information
"""
from typing import Dict, Optional
from backend.api.dependencies import get_ner_extractor
import re


class TextProcessor:
    """Extract and normalize drug information from text."""
    
    KG_TO_LBS = 2.20462
    AGE_CONVERTER = 12
    
    def __init__(self):
        self.ner_extractor = get_ner_extractor()
    
    def process_text(self, text: str, use_ner: bool = True) -> Dict:
        """Extract drug information from text."""
        if not text or not text.strip():
            return {"error": "Empty input"}
        
        if not use_ner:
            return {
                "brand_name": text.strip(),
                "dosage": None,
                "dosage_numeric": None,
                "route": None,
                "form": None,
                "weight_lb": None,
                "age_months": None
            }
        
        entities = self.ner_extractor.extract(text)
        
        drugs = entities.get("drugs", [])
        if not drugs:
            return {"error": "No drug names detected"}
        
        dosages = entities.get("dosages", [])
        weights = entities.get("weights", [])
        ages = entities.get("ages", [])
        routes = entities.get("routes", [])
        forms = entities.get("forms", [])
        
        # Normalize dosage to standard mg/ml format
        normalized_dosage = None
        dosage_numeric = None
        if dosages:
            normalized_dosage = self._normalize_concentration(dosages[0])
            dosage_numeric = self._extract_concentration_value(normalized_dosage)
        
        return {
            "brand_name": drugs[0],
            "dosage": normalized_dosage,
            "dosage_numeric": dosage_numeric,
            "route": routes[0].lower().strip() if routes else None,
            "form": forms[0].lower().strip() if forms else None,
            "weight_lb": self._parse_weight(weights[0]) if weights else None,
            "age_months": self._parse_age(ages[0]) if ages else None
        }
    
    def _normalize_concentration(self, dosage_str: str) -> str:
        """Normalize concentration to standard mg/ml format."""
        if not dosage_str:
            return dosage_str
        
        # Pattern: "5mg/5ml" or "160mg/5ml" - calculate actual concentration
        pattern = r'(\d+\.?\d*)\s*mg\s*/\s*(\d+\.?\d*)\s*ml'
        match = re.search(pattern, dosage_str, re.IGNORECASE)
        
        if match:
            numerator = float(match.group(1))
            denominator = float(match.group(2))
            concentration = numerator / denominator
            
            # Format nicely
            if concentration == int(concentration):
                return f"{int(concentration)} mg/ml"
            else:
                return f"{concentration:.2f} mg/ml"
        
        # Already in "Xmg/ml" format - just clean spacing
        pattern2 = r'(\d+\.?\d*)\s*mg\s*/\s*ml'
        match2 = re.search(pattern2, dosage_str, re.IGNORECASE)
        if match2:
            value = match2.group(1)
            return f"{value} mg/ml"
        
        # Plain "100mg" format
        pattern3 = r'(\d+\.?\d*)\s*mg\b'
        match3 = re.search(pattern3, dosage_str, re.IGNORECASE)
        if match3:
            return f"{match3.group(1)} mg"
        
        return dosage_str
    
    def _extract_concentration_value(self, dosage_str: str) -> Optional[float]:
        """Extract numeric concentration value."""
        if not dosage_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)', dosage_str)
        if match:
            return float(match.group(1))
        return None
    
    def _parse_weight(self, weight_str: str) -> Optional[float]:
        """Parse weight and convert to lbs."""
        if not weight_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)\s*([a-z]+)', weight_str, re.IGNORECASE)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2).lower()
        
        if 'kg' in unit or 'kilo' in unit:
            value = value * self.KG_TO_LBS
        
        return round(value, 2)
    
    def _parse_age(self, age_str: str) -> Optional[int]:
        """Extract age and convert to months."""
        if not age_str:
            return None
        
        match = re.search(r'(\d+)', age_str)
        if not match:
            return None
        
        value = int(match.group(1))
        
        if "month" in age_str.lower():
            return value
        
        return value * self.AGE_CONVERTER