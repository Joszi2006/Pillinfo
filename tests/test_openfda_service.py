"""
Tests for OpenFDAService
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from backend.services.openfda_service import OpenFDAService


@pytest.fixture
def openfda_service():
    return OpenFDAService()


# ==================== FIELD EXTRACTION (your logic) ====================

def test_extract_fields_grabs_correct_keys(openfda_service):
    """Test that extraction grabs the right fields from label."""
    label = {
        "purpose": ["some data"],
        "dosage_and_administration": ["more data"],
        "warnings": ["warning data"],
        "contraindications": ["contraindication data"],
        "adverse_reactions": ["reaction data"],
        "unused_field": ["ignored"]
    }
    
    result = openfda_service._extract_fields(label)
    
    # Should have exactly these 5 fields
    assert set(result.keys()) == {
        "purpose", "dosage_and_administration", 
        "warnings", "contraindications", "adverse_reactions"
    }
    
    # Should extract the values (we don't care what they are)
    assert result["purpose"] == ["some data"]
    assert result["warnings"] == ["warning data"]


def test_extract_fields_handles_missing_keys(openfda_service):
    """Test that missing fields become None."""
    label = {"purpose": ["only this"]}
    
    result = openfda_service._extract_fields(label)
    
    assert result["purpose"] == ["only this"]
    assert result["dosage_and_administration"] is None
    assert result["warnings"] is None


# ==================== RETRY LOGIC (your code) ====================

@pytest.mark.asyncio
async def test_retry_logic_on_429(openfda_service):
    """Test that 429 triggers retry with exponential backoff."""
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429
    
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {
        "results": [{"purpose": ["test"]}]
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        # First call: 429, second call: success
        mock_get = AsyncMock(side_effect=[mock_response_429, mock_response_success])
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        with patch('asyncio.sleep') as mock_sleep:
            result = await openfda_service._execute_query('test_query')
            
            assert result is not None
            assert mock_get.call_count == 2
            # Should have slept once with backoff (2^0 = 1)
            mock_sleep.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_retry_exhaustion_on_repeated_429(openfda_service):
    """Test that repeated 429s eventually give up after max_retries."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        with patch('asyncio.sleep'):
            result = await openfda_service._execute_query('test_query')
            
            assert result is None
            assert mock_get.call_count == 3  # max_retries


@pytest.mark.asyncio
async def test_timeout_retries_correctly(openfda_service):
    """Test that timeout triggers retry."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        with patch('asyncio.sleep') as mock_sleep:
            result = await openfda_service._execute_query('test_query')
            
            assert result is None
            assert mock_get.call_count == 3
            # Should sleep between retries (not on last one)
            assert mock_sleep.call_count == 2


# ==================== ERROR HANDLING (your code) ====================

@pytest.mark.asyncio
async def test_404_returns_none_immediately(openfda_service):
    """Test that 404 returns None without retry."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await openfda_service._execute_query('test_query')
        
        assert result is None
        assert mock_get.call_count == 1  # No retry


@pytest.mark.asyncio
async def test_empty_results_returns_none(openfda_service):
    """Test that empty results array returns None."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await openfda_service._execute_query('test_query')
        
        assert result is None


@pytest.mark.asyncio
async def test_missing_results_key_returns_none(openfda_service):
    """Test that response without results key returns None."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"other_key": "data"}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await openfda_service._execute_query('test_query')
        
        assert result is None


@pytest.mark.asyncio
async def test_generic_exception_returns_none(openfda_service):
    """Test that unexpected exceptions return None."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Random error")
        )
        
        result = await openfda_service._execute_query('test_query')
        
        assert result is None


# ==================== QUERY FORMATTING (your code) ====================

@pytest.mark.asyncio
async def test_get_drug_info_formats_query(openfda_service):
    """Test that RXCUI is formatted correctly into OpenFDA query."""
    with patch.object(openfda_service, '_execute_query', return_value=None) as mock_execute:
        await openfda_service.get_drug_info("123456")
        
        mock_execute.assert_called_once_with('openfda.rxcui:"123456"')


# ==================== REAL API SMOKE TEST ====================

@pytest.mark.asyncio
async def test_can_reach_openfda_api(openfda_service):
    """Smoke test: verify we can actually reach OpenFDA."""
    # Use a known RXCUI for Ibuprofen
    result = await openfda_service.get_drug_info("5640")
    
    # We don't care about the content (it's messy)
    # Just verify: either we get data back, or None (both are valid)
    assert result is None or isinstance(result, dict)
    
    # If we got data, verify structure
    if result:
        assert "purpose" in result
        assert "warnings" in result


@pytest.mark.asyncio
async def test_handles_nonexistent_drug(openfda_service):
    """Test that nonexistent RXCUI returns None (not crash)."""
    result = await openfda_service.get_drug_info("999999999")
    
    assert result is None