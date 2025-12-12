"""
Tests for DosageService
"""
import pytest
from unittest.mock import patch
from backend.services.dosage_service import DosageService


@pytest.fixture
def dosage_service():
    return DosageService()


# ==================== RANGE MATCHING (core logic) ====================

def test_in_range_basic_cases(dosage_service):
    """Test range matching logic."""
    # Within range
    assert dosage_service._in_range(25, 20, 30) is True
    # Outside range
    assert dosage_service._in_range(35, 20, 30) is False
    # No bounds
    assert dosage_service._in_range(25, None, None) is False
    # Only max
    assert dosage_service._in_range(25, None, 30) is True


# ==================== CONCENTRATION EXTRACTION ====================

def test_extract_concentration(dosage_service):
    """Test extracting mg/ml from product name."""
    assert dosage_service._extract_concentration("Ibuprofen 100 MG/ML") == 100.0
    assert dosage_service._extract_concentration("Drug 40.5 mg/ml") == 40.5
    assert dosage_service._extract_concentration("Tablet") is None


# ==================== DOSE FINDING LOGIC ====================

def test_find_dose_perfect_match(dosage_service):
    """Test when weight and age match same row."""
    product = {"product_name": "Drug 100 MG/ML"}
    chart = [{"min_weight_lb": 20, "max_weight_lb": 30, 
              "min_age_months": 12, "max_age_months": 24, "dose_ml": 5.0}]
    
    result = dosage_service._find_dose_from_chart(product, chart, 25, 18)
    
    assert result["dose"] == "5.0 mL"
    assert result["warning"] is None


def test_find_dose_weight_only(dosage_service):
    """Test weight match without age."""
    product = {"product_name": "Drug"}
    chart = [{"min_weight_lb": 20, "max_weight_lb": 30, "dose_ml": 5.0}]
    
    result = dosage_service._find_dose_from_chart(product, chart, 25, None)
    
    assert result["dose"] == "5.0 mL"


def test_find_dose_age_only_has_warning(dosage_service):
    """Test age-only match includes warning."""
    product = {"product_name": "Drug"}
    chart = [{"min_age_months": 12, "max_age_months": 24, "dose_ml": 5.0}]
    
    result = dosage_service._find_dose_from_chart(product, chart, None, 18)
    
    assert result["dose"] == "5.0 mL"
    assert "less accurate" in result["warning"]


def test_find_dose_mismatch_triggers_calculation(dosage_service):
    """Test weight/age in different rows triggers calculation."""
    product = {"product_name": "Drug 100 MG/ML"}
    chart = [
        {"min_weight_lb": 40, "max_weight_lb": 50, "dose_ml": 7.0},
        {"min_age_months": 12, "max_age_months": 24, "dose_ml": 5.0}
    ]
    
    with patch.object(dosage_service, '_calculate_exact_dose', return_value="6.5 mL"):
        result = dosage_service._find_dose_from_chart(product, chart, 40, 18)
        
        assert result["dose"] == "6.5 mL"
        assert "Weight exceeds typical range" in result["warning"]


def test_find_dose_no_match_returns_none(dosage_service):
    """Test no matching rows returns None."""
    product = {"product_name": "Drug"}
    chart = [{"min_weight_lb": 20, "max_weight_lb": 30, "dose_ml": 5.0}]
    
    result = dosage_service._find_dose_from_chart(product, chart, 50, None)
    
    assert result is None