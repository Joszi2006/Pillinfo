"""
RxNorm Service - Minimal Version
Single Responsibility: Fetch drug info from RxNorm API
"""
import httpx
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class RxNormService:
    """
    Minimal RxNorm service - only essential methods.
    Gets drug products and generic names.
    """
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    TIMEOUT = 10
    
    def __init__(self):
        self.timeout = httpx.Timeout(self.TIMEOUT)
        self.headers = {"User-Agent": "DrugLookupSystem/1.0"}
    
    async def get_drug_details(self, brand_name: str) -> Optional[Dict]:
        """
        Get comprehensive drug details.
        THIS IS THE ONLY PUBLIC METHOD YOU NEED!
        
        Args:
            brand_name: Brand name to look up
        
        Returns:
            {
                "brand_name": str,
                "generic_name": str,
                "rxcui": str,
                "products": [
                    {"name": str, "rxcui": str, "tty": str}
                ]
            }
            or None if not found
        """
        # Get products
        products = await self._fetch_products(brand_name)
        
        if not products:
            return None
        
        # Get generic name
        generic_name = await self._get_generic_name(products[0]["rxcui"])
        
        return {
            "brand_name": brand_name,
            "generic_name": generic_name,
            "rxcui": products[0]["rxcui"],
            "products": products
        }
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    async def _fetch_products(self, brand_name: str) -> List[Dict]:
        """
        Fetch drug products from RxNorm API.
        PRIVATE - only called by get_drug_details()
        """
        url = f"{self.BASE_URL}/drugs.json"
        params = {"name": brand_name}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.headers
                )
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
        """
        Get generic name from RXCUI.
        PRIVATE - only called by get_drug_details()
        """
        url = f"{self.BASE_URL}/rxcui/{rxcui}/related.json"
        params = {"tty": "IN+MIN"}  # IN = ingredient
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.headers
                )
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
        """
        Parse RxNorm API response.
        PRIVATE - only called by _fetch_products()
        """
        products = []
        seen_names = set()
        
        concept_groups = data.get("drugGroup", {}).get("conceptGroup", [])
        
        for group in concept_groups:
            tty = group.get("tty", "")
            if tty in ["SBD", "BN", "SCD", "BPCK", "GPCK"]:
                for concept in group.get("conceptProperties", []):
                    name = concept.get("synonym") or concept.get("name")
                    rxcui = concept.get("rxcui")
                    
                    if name and rxcui and name not in seen_names:
                        products.append({
                            "name": name,
                            "rxcui": rxcui,
                            "tty": tty
                        })
                        seen_names.add(name)
        
        return products