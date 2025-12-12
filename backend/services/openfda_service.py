"""
OpenFDA Service - Fetches raw drug information from FDA API
"""
import httpx
import asyncio
import os
from typing import Dict, Optional
from config import OPENFDA_API_KEY, OPENFDA_BASE_URL, OPENFDA_TIMEOUT
import asyncio



class OpenFDAService:
    """Query OpenFDA drug label database by RXCUI."""
    
    def __init__(self):
        self.base_url = OPENFDA_BASE_URL
        self.timeout = OPENFDA_TIMEOUT
        self.max_retries = 3
        self.api_key = OPENFDA_API_KEY
    
    async def get_drug_info(self, rxcui: str) -> Optional[Dict]:
        """Get raw drug info by RXCUI."""
        query = f'openfda.rxcui:"{rxcui}"'
        return await self._execute_query(query)
    
    async def _execute_query(self, query: str) -> Optional[Dict]:
        """Execute OpenFDA query with retry logic."""
        params = {
            "search": query,
            "limit": 1,
            "api_key": self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(self.base_url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "results" in data and data["results"]:
                            return self._extract_fields(data["results"][0])
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
    
    def _extract_fields(self, label: Dict) -> Dict:
        """Extract raw fields from FDA label."""
        return {
            "purpose": label.get("purpose"),
            "dosage_and_administration": label.get("dosage_and_administration"),
            "warnings": label.get("warnings"),
            "contraindications": label.get("contraindications"),
            "adverse_reactions": label.get("adverse_reactions")
        }
    