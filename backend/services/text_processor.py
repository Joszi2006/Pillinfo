"""
Text Processor Service - SHARED by both text and image streams
Single Responsibility: Process text through NER + Fuzzy matching + Data transformation
"""
from typing import Dict, Optional, List
from backend.ml.ner_extractor import NERExtractor
from backend.ml.fuzzy_matcher import FuzzyMatcher
import re

MIN_WEIGHT_KG = 1.0
MAX_WEIGHT_KG = 500.0
MIN_AGE_YEARS = 0
MAX_AGE_YEARS = 120
LBS_TO_KG_CONVERSION = 0.453592

class TextProcessor:
    
    def __init__(self):
        self.ner_extractor = NERExtractor()
        self.fuzzy_matcher = FuzzyMatcher()
    
    def process_text(self, text: str, use_ner: bool = True) -> Dict:
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
        
        entities = self.ner_extractor.extract(text)
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
        
        extracted_drug = drugs[0]
        correction = self.fuzzy_matcher.correct_drug_name(extracted_drug)
        final_drug_name = correction["corrected"] if correction["matched"] else extracted_drug
        
        dosages = entities.get("dosages", [])
        weights = entities.get("weights", [])
        ages = entities.get("ages", [])
        routes = entities.get("routes", [])
        forms = entities.get("forms", [])
        
        dosage_str = dosages[0] if dosages else None
        weight_str = weights[0] if weights else None
        age_str = ages[0] if ages else None
        route = self._normalize_route(routes[0]) if routes else None
        form = self._normalize_form(forms[0]) if forms else None
        
        dosage_numeric = self._extract_dosage_numeric(dosage_str)
        dosage_normalized = self._normalize_dosage(dosage_str)
        weight_kg = self._convert_weight_to_kg(weight_str)
        age_years = self._convert_age_to_years(age_str)
        
        return {
            "brand_name": final_drug_name,
            "dosage": dosage_normalized,
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
        if not dosage_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)', dosage_str)
        if match:
            value = float(match.group(1))
            if 0.01 <= value <= 10000:
                return value
        return None
    
    def _normalize_dosage(self, dosage_str: str) -> Optional[str]:
        if not dosage_str:
            return None
        
        # Extract number and unit parts
        match = re.search(r'(\d+\.?\d*)\s*([a-zA-Z/]+)', dosage_str, re.IGNORECASE)
        if not match:
            return None
        
        number = match.group(1)
        unit = match.group(2).lower()
        
        # Remove any spaces around the slash in compound units
        unit = re.sub(r'\s*/\s*', '/', unit)
        
        # Return in format: "number unit" (e.g., "40 mg/ml")
        return f"{number} {unit}"
    
    def _normalize_route(self, route: str) -> Optional[str]:
        if not route:
            return None
        return route.lower().strip()
    
    def _normalize_form(self, form: str) -> Optional[str]:
        if not form:
            return None
        return form.lower().strip()
    
    def _convert_weight_to_kg(self, weight_str: str) -> Optional[float]:
        if not weight_str:
            return None
        
        match = re.search(r'(\d+\.?\d*)\s*([a-z]+)', weight_str, re.IGNORECASE)
        if not match:
            return None
        
        value = float(match.group(1))
        unit = match.group(2).lower()
        
        if 'lb' in unit or 'pound' in unit:
            value = value * LBS_TO_KG_CONVERSION
        
        if MIN_WEIGHT_KG <= value <= MAX_WEIGHT_KG:
            return round(value, 2)
        return None
    
    def _convert_age_to_years(self, age_str: str) -> Optional[int]:
        if not age_str:
            return None
        
        match = re.search(r'(\d+)', age_str)
        if not match:
            return None
        
        age = int(match.group(1))
        
        if MIN_AGE_YEARS <= age <= MAX_AGE_YEARS:
            return age
        return None
    
    def inject_cache(self, cache_dict: Dict):
        self.fuzzy_matcher.set_cache(cache_dict)