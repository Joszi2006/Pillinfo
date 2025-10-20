"""
OpenFDA Service - Ultra Minimal
Single Responsibility: Fetch official drug information from OpenFDA API
"""
import httpx
from typing import Dict, Optional
import asyncio


class OpenFDAService:
    """Service for querying OpenFDA drug label database."""
    
    BASE_URL = "https://api.fda.gov/drug/label.json"
    TIMEOUT = 10
    MAX_RETRIES = 3
    
    def __init__(self, timeout: int = TIMEOUT, max_retries: int = MAX_RETRIES):
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def get_drug_info(
        self,
        drug_name: str,
        generic_name: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get comprehensive drug information from FDA.
        ONE CALL GETS EVERYTHING - purpose, dosing, warnings, etc.
        
        Args:
            drug_name: Brand name (e.g., "Tylenol")
            generic_name: Generic name (e.g., "acetaminophen") 
        
        Returns:
            Dictionary with ALL drug information or None if not found
        """
        if not drug_name or not drug_name.strip():
            return None
        
        # Build OpenFDA query
        if generic_name:
            query = f'openfda.brand_name:"{drug_name}" AND openfda.generic_name:"{generic_name}"'
        else:
            query = f'openfda.brand_name:"{drug_name}"'
        
        params = {"search": query, "limit": 1}
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.BASE_URL, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "results" in data and data["results"]:
                            return self._parse_label(data["results"][0], drug_name)
                        
                        return None
                    
                    elif response.status_code == 404:
                        return None
                    
                    elif response.status_code == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    else:
                        return None
            
            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                return None
            
            except Exception:
                return None
        
        return None
    
    def _parse_label(self, label: Dict, search_term: str) -> Dict:
        """Parse FDA drug label into structured format."""
        openfda = label.get("openfda", {})
        
        return {
            # Clinical information
            "purpose": self._extract_field(label, "purpose"),
            # "indications_and_usage": self._extract_field(label, "indications_and_usage"),
            "dosage_and_administration": self._extract_field(label, "dosage_and_administration"),
            "pediatric_use": self._extract_field(label, "pediatric_use"),
            # Safety information
            "warnings": self._extract_field(label, "warnings"),
            "contraindications": self._extract_field(label, "contraindications"),
            "adverse_reactions": self._extract_field(label, "adverse_reactions")
        }
    
    def _extract_field(self, label: Dict, field: str) -> Optional[str]:
        """Extract field from FDA label, handling list format."""
        value = label.get(field)
        
        if value is None:
            return None
        
        if isinstance(value, list):
            if not value:
                return None
            return " ".join(str(item) for item in value)
        
        return str(value)