"""
Integration tests for NERExtractor
"""
import pytest
from backend.api.dependencies import get_ner_extractor


@pytest.fixture(scope="module")
def ner_extractor():
    return get_ner_extractor()


# ==================== WEIGHT EXTRACTION ====================

def test_extract_weights_common_formats(ner_extractor):
    """Test common weight formats."""
    text = "Child: 25kg, Adult: 70.5 kilograms, Baby: 15 lbs, Teen: 120 pounds"
    weights = ner_extractor._extract_weights(text)
    
    assert "25kg" in weights
    assert "70.5 kilograms" in weights
    assert "15 lbs" in weights
    assert "120 pounds" in weights


def test_extract_weights_with_spaces(ner_extractor):
    """Test weights with spaces between number and unit."""
    weights = ner_extractor._extract_weights("Patient weighs 25 kg")
    assert "25 kg" in weights


def test_extract_weights_case_insensitive(ner_extractor):
    """Test case insensitive matching."""
    weights = ner_extractor._extract_weights("Weight: 25KG and 50LBS")
    # Should match regardless of case
    assert len(weights) == 2


def test_extract_weights_no_match(ner_extractor):
    """Test when no weights present."""
    weights = ner_extractor._extract_weights("No weight information")
    assert weights == []


# ==================== AGE EXTRACTION ====================

def test_extract_ages_common_formats(ner_extractor):
    """Test common age formats."""
    text = "5 years old, age: 3, 18 months old, 2.5 yrs"
    ages = ner_extractor._extract_ages(text)
    
    # Check each format was extracted
    assert any("5" in age and "year" in age for age in ages)
    assert any("3" in age for age in ages)
    assert any("18" in age and "month" in age for age in ages)
    assert any("2.5" in age for age in ages)


def test_extract_ages_deduplication(ner_extractor):
    """Test that duplicates are removed."""
    text = "5 years old, 5 years old"
    ages = ner_extractor._extract_ages(text)
    
    assert len(ages) == 1


def test_extract_ages_case_insensitive(ner_extractor):
    """Test case insensitive matching."""
    ages = ner_extractor._extract_ages("Age: 5 YEARS OLD")
    assert "5 YEARS OLD" in ages


def test_extract_ages_no_match(ner_extractor):
    """Test when no ages present."""
    ages = ner_extractor._extract_ages("No age information")
    assert ages == []


# ==================== FULL INTEGRATION ====================

def test_extract_returns_all_fields(ner_extractor):
    """Test that all expected fields are present."""
    result = ner_extractor.extract("Simple text")
    
    required_fields = ["drugs", "dosages", "routes", "forms", "weights", "ages"]
    for field in required_fields:
        assert field in result
        assert isinstance(result[field], list)


def test_extract_combines_gliner_and_regex(ner_extractor):
    """Test that GLiNER entities and regex patterns work together."""
    text = "Give Advil 200mg to patient (25kg, 5 years old)"
    
    result = ner_extractor.extract(text)
    
    # Check actual extracted values
    assert "Advil" in result["drugs"]
    assert "25kg" in result["weights"]
    assert any("5" in age and "year" in age for age in result["ages"])


def test_extract_realistic_prescription(ner_extractor):
    """Test with realistic prescription text."""
    text = "Amoxicillin 250mg capsules, oral, for 5 year old child weighing 20kg"
    
    result = ner_extractor.extract(text)
    
    # Verify actual extracted values
    assert "Amoxicillin" in result["drugs"]
    assert "20kg" in result["weights"]
    assert any("5" in age for age in result["ages"])