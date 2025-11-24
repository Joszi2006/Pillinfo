"""
Tests for RxNormService
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from backend.services.drug_lookup.rxnorm_service import RxNormService


@pytest.fixture
def rxnorm_service():
    return RxNormService()


# ==================== PARSING LOGIC ====================

def test_parse_extracts_name_and_rxcui(rxnorm_service):
    """Core parsing: extract name and rxcui."""
    data = {
        "drugGroup": {
            "conceptGroup": [{
                "conceptProperties": [
                    {"name": "Advil 200mg", "rxcui": "123"}
                ]
            }]
        }
    }
    
    products = rxnorm_service._parse_products(data)
    
    assert products == [{"name": "Advil 200mg", "rxcui": "123"}]


def test_parse_uses_synonym_fallback(rxnorm_service):
    """Use synonym when name is missing."""
    data = {
        "drugGroup": {
            "conceptGroup": [{
                "conceptProperties": [
                    {"synonym": "Ibuprofen", "rxcui": "456"}
                ]
            }]
        }
    }
    
    products = rxnorm_service._parse_products(data)
    
    assert products[0]["name"] == "Ibuprofen"


def test_parse_filters_missing_rxcui(rxnorm_service):
    """Products without rxcui should be filtered out."""
    data = {
        "drugGroup": {
            "conceptGroup": [{
                "conceptProperties": [
                    {"name": "Has RXCUI", "rxcui": "123"},
                    {"name": "No RXCUI"},
                ]
            }]
        }
    }
    
    products = rxnorm_service._parse_products(data)
    
    assert len(products) == 1
    assert products[0]["rxcui"] == "123"


def test_parse_filters_missing_name_and_synonym(rxnorm_service):
    """Products without name or synonym should be filtered out."""
    data = {
        "drugGroup": {
            "conceptGroup": [{
                "conceptProperties": [
                    {"rxcui": "123"},  # No name or synonym
                    {"name": "Valid", "rxcui": "456"}
                ]
            }]
        }
    }
    
    products = rxnorm_service._parse_products(data)
    
    assert len(products) == 1


def test_parse_handles_empty_response(rxnorm_service):
    """Empty response returns empty list."""
    data = {"drugGroup": {"conceptGroup": []}}
    
    products = rxnorm_service._parse_products(data)
    
    assert products == []


def test_parse_handles_missing_keys(rxnorm_service):
    """Malformed response doesn't crash."""
    assert rxnorm_service._parse_products({}) == []
    assert rxnorm_service._parse_products({"drugGroup": {}}) == []


# ==================== ERROR HANDLING ====================

@pytest.mark.asyncio
async def test_fetch_returns_empty_on_timeout(rxnorm_service):
    """Timeout returns empty list, not exception."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        
        products = await rxnorm_service._fetch_products("Advil")
        
        assert products == []


@pytest.mark.asyncio
async def test_fetch_returns_empty_on_http_error(rxnorm_service):
    """HTTP errors return empty list."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=MagicMock()
    )
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        products = await rxnorm_service._fetch_products("FakeDrug")
        
        assert products == []


@pytest.mark.asyncio
async def test_fetch_returns_empty_on_any_exception(rxnorm_service):
    """Any exception returns empty list."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Random error")
        )
        
        products = await rxnorm_service._fetch_products("Advil")
        
        assert products == []


# ==================== PUBLIC INTERFACE ====================

@pytest.mark.asyncio
async def test_get_drug_details_returns_none_when_empty(rxnorm_service):
    """No products = return None."""
    with patch.object(rxnorm_service, '_fetch_products', return_value=[]):
        result = await rxnorm_service.get_drug_details("FakeDrug")
        
        assert result is None


@pytest.mark.asyncio
async def test_get_drug_details_returns_correct_structure(rxnorm_service):
    """Returns dict with brand_name and products."""
    mock_products = [{"name": "Advil", "rxcui": "123"}]
    
    with patch.object(rxnorm_service, '_fetch_products', return_value=mock_products):
        result = await rxnorm_service.get_drug_details("Advil")
        
        assert result == {
            "brand_name": "Advil",
            "products": mock_products
        }


@pytest.mark.asyncio
async def test_full_flow(rxnorm_service):
    """Test complete flow from API response to final output."""
    api_response = {
        "drugGroup": {
            "conceptGroup": [{
                "conceptProperties": [
                    {"name": "Advil 200mg", "rxcui": "123"},
                    {"synonym": "Ibuprofen", "rxcui": "456"},
                    {"name": "Missing RXCUI"}  # Should be filtered
                ]
            }]
        }
    }
    
    mock_response = MagicMock()
    mock_response.json.return_value = api_response
    mock_response.raise_for_status = MagicMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await rxnorm_service.get_drug_details("Advil")
        
        assert result["brand_name"] == "Advil"
        assert len(result["products"]) == 2
        assert result["products"][0] == {"name": "Advil 200mg", "rxcui": "123"}
        assert result["products"][1] == {"name": "Ibuprofen", "rxcui": "456"}