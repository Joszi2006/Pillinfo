"""
NER Extractor - Medical entity extraction using GLiNER
"""
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from typing import Dict, List
from gliner import GLiNER
import re


class NERExtractor:
    """Extract medical entities using GLiNER with regex fallbacks."""
    
    def __init__(self, model_name: str = "anthonyyazdaniml/gliner-biomed-large-v1.0-medication-regimen-ner"):
        self.model_name = model_name
        self.model = None
    
    def _lazy_load(self):
        """Load GLiNER model on first use."""
        if self.model is None:
            print(f"Loading GLiNER: {self.model_name}...")
            self.model = GLiNER.from_pretrained(self.model_name)
            print("Model loaded successfully")
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities from text."""
        self._lazy_load()
        
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
        
        dosages.extend(self._extract_dosages(text))
        routes.extend(self._extract_routes(text))
        forms.extend(self._extract_forms(text))
        
        return {
            "drugs": list(dict.fromkeys(drugs)),
            "dosages": list(dict.fromkeys(dosages)),
            "routes": list(dict.fromkeys(routes)),
            "forms": list(dict.fromkeys(forms)),
            "weights": self._extract_weights(text),
            "ages": self._extract_ages(text)
        }
    
    def _extract_dosages(self, text: str) -> List[str]:
        """Extract dosage patterns."""
        pattern = r'\b\d+\.?\d*\s?(mg|mcg|ml|g|mg/ml|units?)\b'
        return [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]
    
    def _extract_weights(self, text: str) -> List[str]:
        """Extract weight patterns."""
        pattern = r'\d+\.?\d*\s?(kg|kilograms?|lbs?|pounds?)\b'
        return [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]
    
    def _extract_ages(self, text: str) -> List[str]:
        """Extract age patterns."""
        patterns = [
            r'\d+\s+years?\s+old',
            r'\d+\s+years?(?!\s+old)',
            r'age\s+\d+'
        ]
        matches = []
        for pattern in patterns:
            matches.extend([m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)])
        return matches
    
    def _extract_routes(self, text: str) -> List[str]:
        """Extract administration routes."""
        pattern = r'\b(oral|orally|intravenous|intravenously|iv|topical|topically|' \
                  r'subcutaneous|intramuscular|im|sublingual|rectal|nasal|inhaled|' \
                  r'transdermal|ophthalmic|otic|vaginal|buccal)\b'
        return [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]
    
    def _extract_forms(self, text: str) -> List[str]:
        """Extract medication forms."""
        pattern = r'\b(tablet|tablets|tab|capsule|capsules|cap|syrup|solution|' \
                  r'suspension|injection|injectable|cream|ointment|gel|patch|' \
                  r'powder|granules|drops|spray|inhaler|suppository|lozenge)\b'
        return [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]