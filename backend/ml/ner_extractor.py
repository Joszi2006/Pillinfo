"""
NER Extractor - Medical entity extraction using GLiNER
"""

from typing import Dict, List
from gliner import GLiNER
import re
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class NERExtractor:
    """Extract medical entities using GLiNER with regex fallbacks."""
    
    def __init__(self, model_name: str = "anthonyyazdaniml/gliner-biomed-large-v1.0-medication-regimen-ner"):
        self.model_name = model_name
        self.model = None
        self._lazy_load()
        
    def _lazy_load(self):
        """Load GLiNER model on first use."""
        if self.model is None:
            self.model = GLiNER.from_pretrained(self.model_name)
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities from text."""
        labels = ["medication", "dosage", "route", "form"]
        entities = self.model.predict_entities(text, labels, threshold=0.4)
        
        drugs = []
        dosages = []
        routes = []
        forms = []
        
        for ent in entities:
            label = ent["label"].lower()
            text_val = ent["text"].strip()
            
            if label == "medication":
                drugs.extend(text_val.split())
            elif label == "dosage":
                dosages.append(text_val)
            elif label == "route":
                routes.append(text_val)
            elif label == "form":
                forms.append(text_val)

        
        return {
            "drugs": list(dict.fromkeys(drugs)),
            "dosages": list(dict.fromkeys(dosages)),
            "routes": list(dict.fromkeys(routes)),
            "forms": list(dict.fromkeys(forms)),
            "weights": self._extract_weights(text),
            "ages": self._extract_ages(text)
        }
    
    
    def _extract_weights(self, text: str) -> List[str]:
        """Extract weight patterns."""
        pattern = r'\d+\.?\d*\s?(kg|kilograms?|lbs?|pounds?)\b'
        return [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]
    
    def _extract_ages(self, text: str) -> List[str]:
        """Extract age patterns (years and months)."""
        patterns = [
            r'\d+(?:\.\d+)?\s*(?:years?|yrs?)(?:\s*old)?',
            r'\d+(?:\.\d+)?\s*(?:months?|mos?)(?:\s*old)?',
            r'(?:age[:\s]+)(\d+(?:\.\d+)?)',  # Changed: capture group for just the number
            r'\d+(?:\.\d+)?\s*(?:year|yr|month|mo)\s+old'
        ]
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # If there's a group (like in age pattern), use group 1, otherwise group 0
                extracted = match.group(1) if match.lastindex else match.group(0)
                matches.append(extracted)
        
        # Deduplicate
        seen = set()
        unique = []
        for match in matches:
            normalized = match.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique.append(match)
        
        return unique
        