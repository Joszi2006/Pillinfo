"""
NER Extractor - MedSpacy inference only
Single Responsibility: Extract medical entities from text
"""
import spacy
import medspacy
from typing import Dict, List
from medspacy.ner import TargetRule
class NERExtractor:
    """
    Extracts medical entities using MedSpacy.
    Handles model loading and inference only.
    Training is separate (see backend/models/train_medspacy.py)
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize NER extractor.
        
        Args:
            model_path: Path to custom trained model (optional)
                       If None, uses default MedSpacy model
        """
        self.nlp = None
        self.model_path = model_path
        self._lazy_load()
    
    def _lazy_load(self):
        """Lazy load the model to avoid loading on import."""
        if self.nlp is None:
            if self.model_path:
                # Load custom trained model
                self.nlp = spacy.load(self.model_path)
            else:
                # Load default MedSpacy
                self.nlp = medspacy.load()
                self._add_custom_patterns()
    
    def _add_custom_patterns(self):
        """Add custom entity patterns for drug-specific recognition."""
        # Add common drug names to target matcher
        if "medspacy_target_matcher" in self.nlp.pipe_names:
            target_matcher = self.nlp.get_pipe("medspacy_target_matcher")
            
            # Common drug brand names
            common_drugs = [
                "Advil", "Tylenol", "Aspirin", "Lipitor", "Metformin",
                "Ibuprofen", "Acetaminophen", "Atorvastatin", "Lisinopril",
                "Amoxicillin", "Albuterol", "Metoprolol", "Amlodipine"
            ]
            
            for drug in common_drugs:
                rule = TargetRule(literal=drug, category="DRUG")
                target_matcher.add(rule)
        
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", last=True)
            
            patterns = [
                # Dosage patterns
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "mg"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "mcg"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "ml"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "g"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": {"IN": ["unit", "units"]}}]},
                
                # Route patterns
                {"label": "ROUTE", "pattern": [{"LOWER": "oral"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "orally"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "intravenous"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "intravenously"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "topical"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "topically"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "injection"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "subcutaneous"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "intramuscular"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": {"IN": ["iv", "im", "sq", "po"]}}]},
                
                # Form patterns
                {"label": "FORM", "pattern": [{"LOWER": {"IN": ["tablet", "tablets", "tab"]}}]},
                {"label": "FORM", "pattern": [{"LOWER": {"IN": ["capsule", "capsules", "cap"]}}]},
                {"label": "FORM", "pattern": [{"LOWER": {"IN": ["syrup", "solution", "suspension"]}}]},
                {"label": "FORM", "pattern": [{"LOWER": {"IN": ["injection", "injectable"]}}]},
            ]
            
            ruler.add_patterns(patterns)
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dictionary with extracted entities:
            {
                "drugs": [...],
                "dosages": [...],
                "routes": [...],
                "forms": [...],
                "all_entities": [...]
            }
        """
        
        doc = self.nlp(text)
        
        drugs = []
        dosages = []
        routes = []
        forms = []
        all_entities = []
        
        for ent in doc.ents:
            entity_info = {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            all_entities.append(entity_info)
            
            # Categorize by type
            if ent.label_ in ["DRUG", "MEDICATION"]:
                drugs.append(ent.text)
            elif ent.label_ == "DOSAGE":
                dosages.append(ent.text)
            elif ent.label_ == "ROUTE":
                routes.append(ent.text)
            elif ent.label_ == "FORM":
                forms.append(ent.text)
        
        # Remove duplicates while preserving order
        drugs = list(dict.fromkeys(drugs))
        dosages = list(dict.fromkeys(dosages))
        routes = list(dict.fromkeys(routes))
        forms = list(dict.fromkeys(forms))
        
        return {
            "drugs": drugs,
            "dosages": dosages,
            "routes": routes,
            "forms": forms,
            "all_entities": all_entities
        }
    
    def extract_batch(self, texts: List[str]) -> List[Dict]:
        """
        Extract entities from multiple texts efficiently.
        
        Args:
            texts: List of text strings
        
        Returns:
            List of extraction results
        """
        
        results = []
        for doc in self.nlp.pipe(texts):
            # Process each doc (implementation similar to extract())
            result = self._process_doc(doc)
            results.append(result)
        
        return results
    
    def _process_doc(self, doc) -> Dict:
        """Helper to process a spaCy Doc object."""
        drugs = []
        dosages = []
        routes = []
        forms = []
        all_entities = []
        
        for ent in doc.ents:
            entity_info = {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            all_entities.append(entity_info)
            
            if ent.label_ in ["DRUG", "MEDICATION"]:
                drugs.append(ent.text)
            elif ent.label_ == "DOSAGE":
                dosages.append(ent.text)
            elif ent.label_ == "ROUTE":
                routes.append(ent.text)
            elif ent.label_ == "FORM":
                forms.append(ent.text)
        
        return {
            "drugs": list(dict.fromkeys(drugs)),
            "dosages": list(dict.fromkeys(dosages)),
            "routes": list(dict.fromkeys(routes)),
            "forms": list(dict.fromkeys(forms)),
            "all_entities": all_entities
        }