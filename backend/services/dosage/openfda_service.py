"""
OpenFDA Service - Fetches drug information from FDA API
"""
import httpx
from typing import Dict, Optional
import asyncio


class OpenFDAService:
    """Query OpenFDA drug label database with smart NDC/text strategy."""
    
    BASE_URL = "https://api.fda.gov/drug/label.json"
    TIMEOUT = 10
    MAX_RETRIES = 3

    def __init__(self, timeout: int = TIMEOUT, max_retries: int = MAX_RETRIES):
        self.timeout = timeout
        self.max_retries = max_retries

    async def get_drug_info(
        self,
        ndc: Optional[str] = None,
        drug_name: Optional[str] = None,
        generic_name: Optional[str] = None,
        dosage: Optional[str] = None,
        form: Optional[str] = None,
        route: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get drug info with NDC if available or Fallback to text-based query if needed
        """
        
        # Try NDC first (primary method)
        if ndc:
            result = await self._query_by_ndc(ndc)
            if result:
                return result
        
        # Fallback to text-based query
        if all([drug_name, generic_name, dosage, form, route]):
            return await self._query_by_text(
                drug_name, generic_name, dosage, form, route
            )
        
        return None

    async def _query_by_ndc(self, ndc: str) -> Optional[Dict]:
        """Query OpenFDA using NDC."""
        query = f'openfda.product_ndc:"{ndc}"'
        print(f"OpenFDA NDC Query: {query}")
        return await self._execute_query(query)

    async def _query_by_text(
        self,
        drug_name: str,
        generic_name: str,
        dosage: str,
        form: str,
        route: str
    ) -> Optional[Dict]:
        """Query OpenFDA using text fields."""
        query = (
            f'openfda.brand_name:"{drug_name.strip()}" '
            f'AND openfda.generic_name:"{generic_name.strip()}" '
            f'AND openfda.strength:"{dosage.strip()}" '
            f'AND openfda.dosage_form:"{form.strip()}" '
            f'AND openfda.route:"{route.strip()}"'
        )
        print(f"OpenFDA Text Query: {query}")
        return await self._execute_query(query)

    async def _execute_query(self, query: str) -> Optional[Dict]:
        """Execute OpenFDA query with retry logic."""
        params = {"search": query, "limit": 1}

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.BASE_URL, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "results" in data and data["results"]:
                            return self._parse_label(data["results"][0])
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
            
            except Exception as e:
                print(f"OpenFDA error: {str(e)}")
                return None

        return None

    def _parse_label(self, label: Dict) -> Dict:
        """Parse FDA drug label into structured format."""
        return {
            "purpose": self._extract_field(label, "purpose"),
            "dosage_and_administration": self._extract_field(label, "dosage_and_administration"),
            "warnings": self._extract_field(label, "warnings"),
            "contraindications": self._extract_field(label, "contraindications"),
            "adverse_reactions": self._extract_field(label, "adverse_reactions"),
            "pediatric_use": self._extract_field(label, "pediatric_use")
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