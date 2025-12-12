"""
NER Extractor - Medical entity extraction using GLiNER with quantization
"""
from typing import Dict, List
from gliner import GLiNER
import torch
import re
import os
from config import NER_MODEL_NAME


os.environ["TOKENIZERS_PARALLELISM"] = "false"

class NERExtractor:
    """Extract medical entities using GLiNER with regex fallbacks."""
    
    def __init__(self):
        self.model_name = NER_MODEL_NAME
        self.model = None
        self._lazy_load()
    
    def _lazy_load(self):
        """Load GLiNER model on first use with CPU quantization."""
        if self.model is None:
            self.model = GLiNER.from_pretrained(
                self.model_name, 
                device_map=torch.device('cpu') 
            )

            # Apply int8 weight-only quantization
            self.model = torch.quantization.quantize_dynamic(
                self.model,
                {torch.nn.Linear}, 
                dtype=torch.qint8 
            )

            self.model.eval()
            
    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities from text."""
        labels = [
            "drug name",
            "active ingredient",
            "dosage",
            "route of administration",
            "dosage form"
        ]
        
        with torch.no_grad():
            entities = self.model.predict_entities(text, labels, threshold=0.4)
        
        drugs = []
        active_ingredients = []
        dosages = []
        routes = []
        forms = []
        
        for ent in entities:
            label = ent["label"].lower()
            text_val = ent["text"].strip()
            
            if label == "drug name":
                cleaned_drug = self._extract_base_brand(text_val)
                drugs.append(cleaned_drug)
            elif label == "active ingredient":
                active_ingredients.append(text_val)
            elif label == "dosage":
                dosages.append(text_val)
            elif label == "route of administration":
                routes.append(text_val)
            elif label == "dosage form":
                forms.append(text_val)
        
        return {
            "drugs": list(dict.fromkeys(drugs)),
            "active_ingredients": list(dict.fromkeys(active_ingredients)),
            "dosages": list(dict.fromkeys(dosages)),
            "routes": list(dict.fromkeys(routes)),
            "forms": list(dict.fromkeys(forms)),
            "weights": self._extract_weights(text),
            "ages": self._extract_ages(text)
        }
    
    def _extract_base_brand(self, drug_name: str) -> str:
        """Extract base brand name by removing pediatric prefixes."""
        prefixes = [
            "Childrens", "Children's", "childrens", "children's",
            "Infant", "Infants", "infant", "infants",
            "Junior", "junior",
            "Pediatric", "pediatric",
            "Baby", "baby"
        ]
        
        for prefix in prefixes:
            if drug_name.startswith(prefix):
                base = drug_name[len(prefix):].strip()
                return base
        
        return drug_name
    
    def _extract_weights(self, text: str) -> List[str]:
        """Extract weight patterns."""
        pattern = r'\d+\.?\d*\s?(kg|kilograms?|lbs?|pounds?)\b'
        return [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]
    
    def _extract_ages(self, text: str) -> List[str]:
        """Extract age patterns (years and months)."""
        patterns = [
            r'\d+(?:\.\d+)?\s*(?:years?|yrs?)(?:\s*old)?',
            r'\d+(?:\.\d+)?\s*(?:months?|mos?)(?:\s*old)?',
            r'(?:age[:\s]+)(\d+(?:\.\d+)?)',
            r'\d+(?:\.\d+)?\s*(?:year|yr|month|mo)\s+old'
        ]
        
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
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
