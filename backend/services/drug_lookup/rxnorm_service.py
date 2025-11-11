"""
RxNorm Service - Drug product lookup with NDC enrichment
"""
import httpx
from typing import Dict, Optional, List
import asyncio
import logging

logger = logging.getLogger(__name__)


class RxNormService:
    """Fetch drug products and NDCs from RxNorm API."""
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    TIMEOUT = 10
    
    def __init__(self):
        self.timeout = httpx.Timeout(self.TIMEOUT)
        self.headers = {"User-Agent": "DrugLookupSystem/1.0"}
    
    async def get_drug_details(self, brand_name: str) -> Optional[Dict]:
        """
        Get comprehensive drug details with NDCs for all products.
        """
        products = await self._fetch_products(brand_name)
        
        if not products:
            return None
        
        # Get generic name from first product
        first_rxcui = products[0]["rxcui"]
        generic_name = await self._get_generic_name(first_rxcui)
        
        # Fetch NDCs for ALL products in parallel
        ndc_tasks = [self.get_ndcs_for_rxcui(p["rxcui"]) for p in products]
        ndc_results = await asyncio.gather(*ndc_tasks)
        
        # Attach NDCs to products
        for product, ndcs in zip(products, ndc_results):
            product["ndc"] = ndcs[0] if ndcs else None
            product["all_ndcs"] = ndcs
        
        return {
            "brand_name": brand_name,
            "generic_name": generic_name,
            "products": products
        }
    
    async def get_ndcs_for_rxcui(self, rxcui: str) -> List[str]:
        """Get all NDCs for an RXCUI."""
        url = f"{self.BASE_URL}/rxcui/{rxcui}/ndcs.json"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                ndcs = data.get("ndcGroup", {}).get("ndcList", {}).get("ndc", [])
                return ndcs if ndcs else []
        
        except Exception as e:
            logger.error(f"Error fetching NDCs for RXCUI {rxcui}: {e}")
            return []
    
    async def _fetch_products(self, brand_name: str) -> List[Dict]:
        """Fetch drug products from RxNorm API."""
        url = f"{self.BASE_URL}/drugs.json"
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
            logger.error(f"Timeout fetching products for '{brand_name}'")
            return []
        
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    async def _get_generic_name(self, rxcui: str) -> Optional[str]:
        """Get generic name from RXCUI."""
        url = f"{self.BASE_URL}/rxcui/{rxcui}/related.json"
        params = {"tty": "IN"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                concept_groups = data.get("relatedGroup", {}).get("conceptGroup", [])
                
                for group in concept_groups:
                    if group.get("tty") in ["IN", "MIN"]:
                        concepts = group.get("conceptProperties", [])
                        if concepts:
                            return concepts[0].get("name")
                
                return None
        
        except Exception as e:
            logger.error(f"Error fetching generic name: {e}")
            return None
    
    def _parse_products(self, data: Dict) -> List[Dict]:
        """Parse RxNorm API response into product list."""
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