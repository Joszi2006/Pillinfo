import pytest
from backend.services.text_processor import TextProcessor

class TestTextProcessor:
    """Test the SHARED text processing logic."""
    
    def setup_method(self):
        """Setup before each test."""
        self.processor = TextProcessor()
        # Inject test cache
        self.processor.inject_cache({
            "Lipitor": ["Lipitor 10mg", "Lipitor 20mg"],
            "Advil": ["Advil 200mg"],
        })
    
    def test_process_text_with_ner(self):
        """Test processing text with NER enabled."""
        result = self.processor.process_text("Lipitor 20mg oral", use_ner=True)
        
        assert "brand_name" in result
        assert "dosage" in result
        assert "route" in result
        assert "entities" in result
    
    def test_process_text_without_ner(self):
        """Test processing text with NER disabled."""
        result = self.processor.process_text("Lipitor", use_ner=False)
        
        assert result["brand_name"] == "Lipitor"
        assert result["entities"] is None
    
    def test_fuzzy_correction(self):
        """Test that fuzzy correction works."""
        # "Lipit0r" should be corrected to "Lipitor"
        result = self.processor.process_text("Lipit0r 20mg", use_ner=True)
        
        assert result["correction"] is not None
        assert result["correction"]["corrected"] == "Lipitor"
    
    def test_empty_text(self):
        """Test with empty text."""
        result = self.processor.process_text("", use_ner=True)
        
        assert result.get("brand_name") is None
        assert "error" in result

