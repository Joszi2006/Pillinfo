"""
RxNorm Service - Drug product lookup
"""
import httpx
import os
import logging
from typing import Dict, Optional, List
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)


class RxNormService:
    """Fetch drug products with RXCUIs from RxNorm API."""
    
    def __init__(self):
        # Load from .env with defaults
        self.base_url = os.getenv("RXNORM_BASE_URL")
        timeout_seconds = int(os.getenv("RXNORM_TIMEOUT"))
        self.timeout = httpx.Timeout(timeout_seconds)
        self.headers = {"User-Agent": "DrugLookupSystem/1.0"}
    
    async def get_drug_details(self, brand_name: str) -> Optional[Dict]:
        """
        Get drug products with RXCUIs.
        RXCUI can be used to query OpenFDA directly.
        """
        products = await self._fetch_products(brand_name)
        
        if not products:
            return None
        
        return {
            "brand_name": brand_name,
            "products": products
        }
    
    async def _fetch_products(self, brand_name: str) -> List[Dict]:
        """Fetch drug products from RxNorm API."""
        url = f"{self.base_url}/drugs.json"
        params = {"name": brand_name}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                products = self._parse_products(data)
                
                logger.info(f"Fetched {len(products)} products for '{brand_name}'")
                return products
        
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching products for '{brand_name}'")
            return []
        
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    def _parse_products(self, data: Dict) -> List[Dict]:
        """Parse RxNorm API response into product list with RXCUIs."""
        products = []
        
        concept_groups = data.get("drugGroup", {}).get("conceptGroup", [])
        
        for group in concept_groups:
            for concept in group.get("conceptProperties", []):
                name = concept.get("synonym") or concept.get("name")
                rxcui = concept.get("rxcui")
                if name and rxcui:
                    products.append({
                        "name": name,
                        "rxcui": rxcui
                    })
        
        return products

