from typing import Optional, Dict

class MessageGenerator:
    """
    Generates SHORT user-facing messages and cleans verbose data.
    Frontend handles full descriptions and formatting.
    """
    
    # ==================== UTILITY FUNCTIONS ====================
    
    @staticmethod
    def truncate_text(text: Optional[str], max_length: int = 200) -> Optional[str]:
        """Truncate verbose text."""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."
    
    @staticmethod
    def extract_key_sentences(text: Optional[str], max_sentences: int = 2) -> Optional[str]:
        """Extract first N sentences."""
        if not text:
            return None
        sentences = text.split('. ')
        return '. '.join(sentences[:max_sentences]) + '.'
    
    # ==================== SHORT GUIDANCE MESSAGES ====================
    
    @staticmethod
    def match_guidance_message(match_type: str, match_count: int = 0) -> Optional[str]:
        """Short guidance for product matching."""
        if match_type == "exact":
            return None
        elif match_type == "multiple":
            return f"Found {match_count} products. Please specify further."
        elif match_type == "none":
            return "No exact match found for your criteria."
        elif match_type == "vague":
            return "Please specify dosage, route, or form for exact results."
        return None
    
    @staticmethod
    def no_drug_detected() -> str:
        return "No drug name detected. Please provide a drug name."
    
    @staticmethod
    def drug_not_found(drug_name: str) -> str:
        return f"'{drug_name}' not found in database."
    
    @staticmethod
    def ocr_failed() -> str:
        return "Could not extract text from image. Please try a clearer photo."
    
    @staticmethod
    def ocr_low_confidence_message(confidence: float, extracted_text: str) -> str:
        """Message for low OCR confidence - helpful, not blaming."""
        return (
            f"We had difficulty reading this image clearly (confidence: {confidence:.0%}). "
            f"Extracted text: '{extracted_text}'. Does this look correct? "
            f"For better results, try retaking with better lighting or a clearer image."
        )
    # ==================== DATA CLEANING ====================
    
    @staticmethod
    def clean_dosage_info(dosage_info: Optional[Dict]) -> Optional[Dict]:
        """Truncate verbose dosage fields."""
        if not dosage_info:
            return None
        
        cleaned = {
            "source": dosage_info.get("source"),
            "confidence": dosage_info.get("confidence"),
            "note": dosage_info.get("note")
        }
        
        if "dosing_info" in dosage_info:
            dosing = dosage_info["dosing_info"]
            if isinstance(dosing, dict):
                cleaned["dosing_info"] = {
                    "dosage_instructions": MessageGenerator.truncate_text(
                        dosing.get("dosage_and_administration"), 300
                    ),
                    "pediatric_use": MessageGenerator.truncate_text(
                        dosing.get("pediatric_use"), 200
                    ),
                    "warnings": MessageGenerator.extract_key_sentences(
                        dosing.get("warnings"), 2
                    )
                }
        
        # Keep calculation results
        for key in ["recommended_dose_mg", "methods", "warnings"]:
            if key in dosage_info:
                cleaned[key] = dosage_info[key]
        
        return cleaned
    
    @staticmethod
    def clean_fda_info(fda_info: Optional[Dict]) -> Optional[Dict]:
        """Truncate verbose FDA fields."""
        if not fda_info:
            return None
        
        return {
            "purpose": fda_info.get("purpose"),
            "dosage_instructions": MessageGenerator.truncate_text(
                fda_info.get("dosage_and_administration"), 400
            ),
            "pediatric_use": MessageGenerator.truncate_text(
                fda_info.get("pediatric_use"), 300
            ),
            "warnings": MessageGenerator.extract_key_sentences(
                fda_info.get("warnings"), 3
            ),
            "contraindications": MessageGenerator.truncate_text(
                fda_info.get("contraindications"), 200
            )
        }