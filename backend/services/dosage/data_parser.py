"""
Data Parser - Clean raw FDA data using Claude
"""
import json
import logging
from typing import Dict
from backend.api.dependencies import get_claude_client
from backend.utilities.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

class DataParser:
    """Parse and clean raw FDA label data using Claude."""
    
    MODEL = "claude-sonnet-4-5-20250929"
    MAX_TOKENS = 2500
    
    def __init__(self):
        self.client = get_claude_client()
    
    def parse_fda_label(self, raw_label: Dict) -> Dict:
        """
        Clean and structure raw FDA label data.
        Returns structured data with dosing_chart as list of dicts.
        """
        if not raw_label:
            return self._empty_response()
        
        prompt = PromptBuilder.fda_label_cleaning(raw_label)
        
        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            cleaned = json.loads(response.content[0].text)
            return self._validate(cleaned)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}")
            return self._empty_response()
        except Exception as e:
            logger.error(f"FDA parsing failed: {e}")
            return self._empty_response()
    
    def _validate(self, data: Dict) -> Dict:
        """Ensure all expected fields exist."""
        return {
            "purpose": data.get("purpose", ""),
            "dosage_instructions": data.get("dosage_instructions", ""),
            "dosing_chart": data.get("dosing_chart", []),
            "warnings": data.get("warnings", ""),
            "contraindications": data.get("contraindications", ""),
            "adverse_reactions": data.get("adverse_reactions", "")
        }
    
    def _empty_response(self) -> Dict:
        """Return empty structure on failure."""
        return {
            "purpose": "",
            "dosage_instructions": "",
            "dosing_chart": [],
            "warnings": "",
            "contraindications": "",
            "adverse_reactions": ""
        }