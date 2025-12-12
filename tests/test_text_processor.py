"""
Tests for TextProcessor
"""
import pytest
from backend.ml.text_processor import TextProcessor


@pytest.fixture(scope="module")
def text_processor():
    return TextProcessor()


# ==================== NUMERIC EXTRACTION ====================

def test_extract_numeric_from_dosage(text_processor):
    """Test extracting numbers from dosage strings."""
    assert text_processor._extract_numeric("200mg") == 200.0
    assert text_processor._extract_numeric("2.5mg") == 2.5
    assert text_processor._extract_numeric("") is None


# ==================== WEIGHT PARSING ====================

def test_parse_weight_kg_to_lbs(text_processor):
    """Test kg converts to lbs."""
    result = text_processor._parse_weight("25kg")
    expected = round(25 * 2.20462, 2)
    assert result == expected


def test_parse_weight_lbs_stays_lbs(text_processor):
    """Test lbs stays as lbs."""
    assert text_processor._parse_weight("50lbs") == 50.0


def test_parse_weight_invalid(text_processor):
    """Test invalid weight returns None."""
    assert text_processor._parse_weight("") is None
    assert text_processor._parse_weight("heavy") is None


# ==================== AGE PARSING ====================

def test_parse_age_years_to_months(text_processor):
    """Test years converts to months."""
    assert text_processor._parse_age("5 years old") == 60


def test_parse_age_months_stays_months(text_processor):
    """Test months stays as months."""
    assert text_processor._parse_age("18 months old") == 18


def test_parse_age_invalid(text_processor):
    """Test invalid age returns None."""
    assert text_processor._parse_age("") is None
    assert text_processor._parse_age("young") is None


# ==================== PROCESS_TEXT ====================

def test_process_text_empty_input(text_processor):
    """Test empty input returns error."""
    assert text_processor.process_text("")["error"] == "Empty input"
    assert text_processor.process_text("   ")["error"] == "Empty input"


def test_process_text_use_ner_false(text_processor):
    """Test use_ner=False returns just brand name."""
    result = text_processor.process_text("Advil", use_ner=False)
    
    assert result["brand_name"] == "Advil"
    assert result["dosage"] is None


def test_process_text_no_drugs_detected(text_processor):
    """Test when no drugs are found."""
    result = text_processor.process_text("The patient is feeling better")
    assert result["error"] == "No drug names detected"


def test_process_text_extracts_all_fields(text_processor):
    """Test full extraction with real prescription text."""
    text = "Give Advil 200mg tablet orally to 5 year old child weighing 25kg"
    result = text_processor.process_text(text)
    
    # Should extract successfully
    assert "error" not in result
    assert result["brand_name"] == "Advil"
    
    # Check structure exists
    expected_fields = ["brand_name", "dosage", "dosage_numeric", 
                      "route", "form", "weight_kg", "age_months"]
    for field in expected_fields:
        assert field in result