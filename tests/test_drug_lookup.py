"""
Tests for DrugLookupService
"""
import pytest
from unittest.mock import patch
from backend.services.drug_lookup_service import DrugLookupService


@pytest.fixture
def drug_lookup_service():
    return DrugLookupService()


# ==================== NORMALIZATION ====================

def test_normalize_basic(drug_lookup_service):
    """Test basic normalization."""
    assert drug_lookup_service._normalize("Advil 200 MG") == "advil 200 mg"


def test_normalize_concentration(drug_lookup_service):
    """Test concentration normalization."""
    result = drug_lookup_service._normalize("40mg/ml")
    assert result == "40 mg ml"
    
    result = drug_lookup_service._normalize("40 mg / ml")
    assert result == "40 mg ml"


def test_normalize_multiple_spaces(drug_lookup_service):
    """Test extra space removal."""
    result = drug_lookup_service._normalize("Advil  200   MG")
    assert result == "advil 200 mg"


# ==================== REFINE PRODUCTS - PERFECT MATCH ====================

def test_refine_products_perfect_match_100(drug_lookup_service):
    """Test that 100% match returns only that product."""
    products = [
        {"name": "Advil 40 MG/ML Oral Suspension"},
        {"name": "Advil 20 MG/ML Oral Suspension"},
        {"name": "Advil 200 MG Oral Tablet"}
    ]
    
    result = drug_lookup_service.refine_products(
        products,
        brand_name="Advil",
        dosage="40 mg/ml",
        form="suspension",
        route="oral"
    )
    
    # Should return ONLY the 40 mg/ml (100% match)
    assert len(result) == 1
    assert "40 MG/ML" in result[0]["name"]


# ==================== REFINE PRODUCTS - CLOSE MATCHES ====================

def test_refine_products_close_matches(drug_lookup_service):
    """Test that close matches within 10 points are returned."""
    products = [
        {"name": "Advil 200 MG Oral Tablet"},
        {"name": "Advil 100 MG Oral Tablet"},
        {"name": "Advil 200 MG Oral Capsule"}
    ]
    
    result = drug_lookup_service.refine_products(
        products,
        brand_name="Advil",
        form="tablet"
    )
    
    # Should return both tablets (close scores)
    assert len(result) == 2
    assert all("Tablet" in p["name"] for p in result)


# ==================== REFINE PRODUCTS - POOR MATCHES ====================

def test_refine_products_poor_match_returns_all(drug_lookup_service):
    """Test that poor matches return all products."""
    products = [
        {"name": "Advil 200 MG Oral Tablet"},
        {"name": "Advil 100 MG Oral Tablet"}
    ]
    
    # Search for something that doesn't match well
    result = drug_lookup_service.refine_products(
        products,
        brand_name="Advil",
        dosage="500mg",  # Doesn't exist
        form="injection"  # Doesn't exist
    )
    
    # Should return all products (poor match)
    assert len(result) == len(products)


# ==================== REFINE PRODUCTS - NO CRITERIA ====================

def test_refine_products_no_criteria_returns_all(drug_lookup_service):
    """Test that no criteria returns all products."""
    products = [
        {"name": "Advil 200 MG Oral Tablet"},
        {"name": "Advil 100 MG Oral Tablet"}
    ]
    
    result = drug_lookup_service.refine_products(
        products,
        brand_name="Advil"
        # No dosage, route, or form
    )
    
    assert result == products


def test_refine_products_empty_list(drug_lookup_service):
    """Test with empty product list."""
    result = drug_lookup_service.refine_products(
        [],
        brand_name="Advil",
        dosage="200mg"
    )
    
    assert result == []


# ==================== REFINE PRODUCTS - FIELD NAME HANDLING ====================

def test_refine_products_handles_product_name_field(drug_lookup_service):
    """Test matching works with product_name field (from database)."""
    products = [
        {"product_name": "Advil 40 MG/ML Oral Suspension"},
        {"product_name": "Advil 20 MG/ML Oral Suspension"}
    ]
    
    result = drug_lookup_service.refine_products(
        products,
        brand_name="Advil",
        dosage="40 mg/ml",
        form="suspension",
        route="oral"  
    )
    
    # Should match correctly even with product_name instead of name
    assert len(result) == 1
    assert "40 MG/ML" in result[0]["product_name"]


# ==================== EVALUATE RESULTS ====================

def test_evaluate_results_single_match(drug_lookup_service):
    """Test single product returns best_match status."""
    refined = [{"name": "Advil 200 MG"}]
    all_products = [{"name": "Advil 200 MG"}, {"name": "Advil 100 MG"}]
    
    result = drug_lookup_service._evaluate_results(refined, all_products)
    
    assert result["status"] == "best_match"
    assert result["product"] == refined[0]
    assert result["products"] == refined


def test_evaluate_results_multiple_matches(drug_lookup_service):
    """Test multiple products returns multiple_matches status."""
    refined = [{"name": "Advil 200 MG"}, {"name": "Advil 100 MG"}]
    all_products = refined
    
    result = drug_lookup_service._evaluate_results(refined, all_products)
    
    assert result["status"] == "multiple_matches"
    assert result["product"] is None
    assert result["products"] == refined


def test_evaluate_results_no_matches(drug_lookup_service):
    """Test empty refined list returns all products."""
    refined = []
    all_products = [{"name": "Advil 200 MG"}, {"name": "Advil 100 MG"}]
    
    result = drug_lookup_service._evaluate_results(refined, all_products)
    
    assert result["status"] == "multiple_matches"
    assert result["product"] is None
    assert result["products"] == all_products


# ==================== LOOKUP_DRUG INTEGRATION ====================

@pytest.mark.asyncio
async def test_lookup_drug_invalid_input(drug_lookup_service):
    """Test empty brand name returns invalid_input."""
    result = await drug_lookup_service.lookup_drug("")
    
    assert result["status"] == "invalid_input"
    assert result["product"] is None
    assert result["products"] == []


@pytest.mark.asyncio
async def test_lookup_drug_strips_whitespace(drug_lookup_service):
    """Test that brand name is stripped."""
    with patch.object(drug_lookup_service, '_fetch_products', return_value=[]):
        result = await drug_lookup_service.lookup_drug("  Advil  ")
        
        # Should strip whitespace
        drug_lookup_service._fetch_products.assert_called_once_with("Advil")


@pytest.mark.asyncio
async def test_lookup_drug_not_found(drug_lookup_service):
    """Test not found returns correct status."""
    with patch.object(drug_lookup_service, '_fetch_products', return_value=[]):
        result = await drug_lookup_service.lookup_drug("NonexistentDrug")
        
        assert result["status"] == "not_found"
        assert result["products"] == []


@pytest.mark.asyncio
async def test_lookup_drug_full_flow(drug_lookup_service):
    """Test complete lookup flow with matching."""
    mock_products = [
        {"rxcui": "123", "name": "Advil 40 MG/ML Oral Suspension"},
        {"rxcui": "456", "name": "Advil 20 MG/ML Oral Suspension"}
    ]
    
    with patch.object(drug_lookup_service, '_fetch_products', return_value=mock_products):
        result = await drug_lookup_service.lookup_drug(
            brand_name="Advil",
            dosage="40 mg/ml",
            form="suspension",
            route="oral"
        )
        
        # Should find perfect match
        assert result["status"] == "best_match"
        assert result["product"]["rxcui"] == "123"