"""
NER Extractor - Hugging Face Medical NER (FIXED VERSION)
Single Responsibility: Extract medical entities from text using pre-trained models
"""
from typing import Dict, List
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re

class NERExtractor:
    """
    Extracts medical entities using Hugging Face pre-trained NER model.
    No manual patterns needed - model already knows medical terminology!
    """
    
    def __init__(self, model_name: str = "Clinical-AI-Apollo/Medical-NER"):
        """
        Initialize NER extractor with Hugging Face model.
        
        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.nlp = None
        self._lazy_load()
    
    def _lazy_load(self):
        """Lazy load the model to avoid loading on import."""
        if self.nlp is None:
            print(f"Loading medical NER model: {self.model_name}...")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForTokenClassification.from_pretrained(self.model_name)
            
            # Create NER pipeline
            self.nlp = pipeline(
                "ner",
                model=model,
                tokenizer=tokenizer,
                aggregation_strategy="simple"  # Merge subword tokens
            )
            
            print("Model loaded successfully!")
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from text using hybrid approach:
        - Primary: Hugging Face NER (ML-based, context-aware)
        - Fallback: Regex patterns (for structured data like dosage/weight/age)
        """
        self._lazy_load()
        
        # Run NER model
        entities = self.nlp(text)
        
        drugs = []
        dosages = []
        routes = []
        forms = []
        all_entities = []
        
        # Step 1: Extract from NER model
        for ent in entities:
            entity_info = {
                "text": ent["word"],
                "label": ent["entity_group"],
                "start": int(ent["start"]),
                "end": int(ent["end"]),
                "score": float(ent["score"])
            }
            all_entities.append(entity_info)
            
            label = ent["entity_group"].upper()
            entity_text = ent["word"].strip()
            
            # Categorize by entity type (using if statements, not elif)
            if any(keyword in label for keyword in ["DRUG", "MEDICATION", "CHEMICAL", "TREATMENT"]):
                drugs.append(entity_text)
            
            if self._is_dosage(entity_text):
                dosages.append(entity_text)
            
            if any(keyword in label for keyword in ["ROUTE", "ADMINISTRATION"]):
                routes.append(entity_text)
            
            if any(keyword in label for keyword in ["FORM", "DOSAGE_FORM"]):
                forms.append(entity_text)
        
        # Step 2: Regex fallback for structured patterns (always run)
        dosages.extend(self._extract_dosages(text))
        weights = self._extract_weights(text)
        ages = self._extract_ages(text)
        
        # Step 3: Regex fallback for routes/forms (always run)
        routes.extend(self._extract_routes_fallback(text))
        forms.extend(self._extract_forms_fallback(text))
        
        # Remove duplicates from all lists
        drugs = list(dict.fromkeys(drugs))
        dosages = list(dict.fromkeys(dosages))
        routes = list(dict.fromkeys(routes))
        forms = list(dict.fromkeys(forms))
        weights = list(dict.fromkeys(weights))
        ages = list(dict.fromkeys(ages))
        
        return {
            "drugs": drugs,
            "dosages": dosages,
            "routes": routes,
            "forms": forms,
            "weights": weights,
            "ages": ages,
            "all_entities": all_entities
        }
    
    def _is_dosage(self, text: str) -> bool:
        """Check if text looks like a dosage."""
        dosage_pattern = r'\d+\.?\d*\s?(mg|mcg|ml|g|mg/ml|units?)\b'
        return bool(re.search(dosage_pattern, text, re.IGNORECASE))
    
    def _extract_dosages(self, text: str) -> List[str]:
        """Extract dosage patterns from text."""
        pattern = r'\d+\.?\d*\s?(mg|mcg|ml|g|mg/ml|units?)\b'
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append(match.group(0))
        return matches
    
    def _extract_weights(self, text: str) -> List[str]:
        """Extract weight patterns from text."""
        pattern = r'\d+\.?\d*\s?(kg|kilograms?|lbs?|pounds?)\b'
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append(match.group(0))
        return matches
    
    def _extract_ages(self, text: str) -> List[str]:
        """Extract age patterns from text (non-overlapping)."""
        patterns = [
            r'\d+\s+years?\s+old',
            r'\d+\s+years?(?!\s+old)',
            r'age\s+\d+',
        ]
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(match.group(0))
        return matches
    
    def _extract_routes_fallback(self, text: str) -> List[str]:
        """
        Regex fallback for route extraction.
        Common administration routes.
        """
        routes_pattern = r'\b(oral|orally|intravenous|intravenously|iv|topical|topically|' \
                        r'subcutaneous|intramuscular|im|sublingual|rectal|nasal|inhaled|' \
                        r'transdermal|ophthalmic|otic|vaginal|buccal)\b'
        matches = []
        for match in re.finditer(routes_pattern, text, re.IGNORECASE):
            matches.append(match.group(0))
        return matches
    
    def _extract_forms_fallback(self, text: str) -> List[str]:
        """
        Regex fallback for form extraction.
        Common medication forms.
        """
        forms_pattern = r'\b(tablet|tablets|tab|capsule|capsules|cap|syrup|solution|' \
                       r'suspension|injection|injectable|cream|ointment|gel|patch|' \
                       r'powder|granules|drops|spray|inhaler|suppository|lozenge)\b'
        matches = []
        for match in re.finditer(forms_pattern, text, re.IGNORECASE):
            matches.append(match.group(0))
        return matches
    
    def extract_batch(self, texts: List[str]) -> List[Dict]:
        """
        Extract entities from multiple texts efficiently.
        
        Args:
            texts: List of text strings
        
        Returns:
            List of extraction results
        """
        self._lazy_load()
        return [self.extract(text) for text in texts]