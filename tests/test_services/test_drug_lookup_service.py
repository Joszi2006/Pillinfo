import pytest
from backend.services.drug_lookup_service import DrugLookupService

class TestDrugLookupService:
    """Test the SIMPLIFIED drug lookup service."""
    
    def setup_method(self):
        """Setup before each test."""
        self.service = DrugLookupService()
    
    @pytest.mark.asyncio
    async def test_lookup_cached_drug(self):
        """Test looking up a drug that's in cache."""
        # First, ensure cache is seeded
        # (In real test, you'd seed cache first)
        
        products, source = await self.service.lookup_drug("Lipitor")
        
        # Should return products
        assert isinstance(products, list)
        assert isinstance(source, str)
    
    @pytest.mark.asyncio
    async def test_lookup_nonexistent_drug(self):
        """Test looking up a drug that doesn't exist."""
        products, source = await self.service.lookup_drug("XYZ123FakeDrug")
        
        assert products == []
        assert "not_found" in source
    
    def test_refine_products_by_dosage(self):
        """Test refining products by dosage."""
        products = [
            "Lipitor 10 MG Oral Tablet",
            "Lipitor 20 MG Oral Tablet",
            "Lipitor 40 MG Oral Tablet"
        ]
        
        refined = self.service.refine_products(products, dosage="20mg")
        
        assert len(refined) > 0
        assert any("20" in p for p in refined)
    
    def test_refine_products_by_route(self):
        """Test refining products by route."""
        products = [
            "Insulin 10 UNIT Injection",
            "Insulin 10 UNIT Oral Tablet"
        ]
        
        refined = self.service.refine_products(products, route="oral")
        
        assert len(refined) > 0
        assert any("oral" in p.lower() for p in refined)
