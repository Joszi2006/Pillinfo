"""
Text Processor Service - SHARED by both text and image streams
Single Responsibility: Process text through NER + Fuzzy matching
"""
from typing import Dict, Optional
from backend.ml.ner_extractor import NERExtractor
from backend.ml.fuzzy_matcher import FuzzyMatcher
from backend.util import log_successful_extraction  # ← Use utility function!

class TextProcessor:
    """
    Processes text through NER and fuzzy matching.
    This is SHARED by both input streams:
    - Stream 1 (Text): User types → TextProcessor
    - Stream 2 (Image): OCR extracts → TextProcessor
    
    Single Responsibility: Extract and correct drug information from text
    """
    
    def __init__(self):
        self.ner_extractor = NERExtractor()
        self.fuzzy_matcher = FuzzyMatcher()
    
    def process_text(self, text: str, use_ner: bool = True, log_success: bool = False) -> Dict:
        """
        Process text through NER and fuzzy correction.
        This is the SHARED logic for both streams!
        
        Args:
            text: Input text (from user OR from OCR)
            use_ner: Whether to use NER extraction
            log_success: Whether to log successful extractions for active learning
        
        Returns:
            Dictionary with extracted and corrected information
        """
        if not use_ner:
            # Simple mode: just return the text as brand name
            return {
                "brand_name": text.strip(),
                "dosage": None,
                "route": None,
                "form": None,
                "entities": None,
                "correction": None
            }
        
        # Step 1: Extract entities with MedSpacy
        entities = self.ner_extractor.extract(text)
        
        if not entities.get("drugs"):
            return {
                "brand_name": None,
                "dosage": None,
                "route": None,
                "form": None,
                "entities": entities,
                "correction": None,
                "error": "No drug names detected"
            }
        
        # Get first extracted drug
        extracted_drug = entities["drugs"][0]
        extracted_dosage = entities["dosages"][0] if entities.get("dosages") else None
        extracted_route = entities["routes"][0] if entities.get("routes") else None
        extracted_form = entities["forms"][0] if entities.get("forms") else None
        
        # Step 2: Correct drug name with fuzzy matching
        correction = self.fuzzy_matcher.correct_drug_name(extracted_drug)
        final_drug_name = correction["corrected"]
        
        result = {
            "brand_name": final_drug_name,
            "dosage": extracted_dosage,
            "route": extracted_route,
            "form": extracted_form,
            "entities": entities,
            "correction": correction,
            "original_text": text
        }
        
        # 🎓 Log successful extraction for Active Learning (using util function!)
        if log_success and final_drug_name:
            log_successful_extraction(
                text=text,
                brand_name=final_drug_name,
                dosage=extracted_dosage,
                route=extracted_route,
                form=extracted_form,
                confidence=correction.get("confidence", 0)
            )
        
        return result
    
    def inject_cache(self, cache_dict: Dict):
        """Inject cache into fuzzy matcher."""
        self.fuzzy_matcher.set_cache(cache_dict)