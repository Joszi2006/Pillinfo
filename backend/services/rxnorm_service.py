"""
RxNorm Service - External API calls only
Single Responsibility: Interact with RxNorm API
"""
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RxNormService:
    """
    Handles all interactions with the RxNorm API.
    No business logic, just API calls and response parsing.
    """
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    TIMEOUT = 5  # seconds
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DrugLookupSystem/1.0"
        })
    
    async def fetch_products(self, brand_name: str) -> List[str]:
        """
        Fetch drug products from RxNorm API.
        
        Args:
            brand_name: Brand name to search for
        
        Returns:
            List of product names
        """
        url = f"{self.BASE_URL}/drugs.json"
        params = {"name": brand_name}
        
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            products = self._parse_products(data)
            
            logger.info(f"Fetched {len(products)} products for '{brand_name}'")
            return products
        
        except requests.Timeout:
            logger.error(f"Timeout fetching products for '{brand_name}'")
            return []
        
        except requests.RequestException as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    def _parse_products(self, data: Dict) -> List[str]:
        """
        Parse RxNorm API response to extract product names.
        
        Args:
            data: JSON response from API
        
        Returns:
            List of unique product names
        """
        products = []
        concept_groups = data.get("drugGroup", {}).get("conceptGroup", [])
        
        for group in concept_groups:
            # Filter by term type (SBD, BN, SCD are drug products)
            if group.get("tty") in ["SBD", "BN", "SCD"]:
                for concept in group.get("conceptProperties", []):
                    name = concept.get("synonym") or concept.get("name")
                    if name and name not in products:
                        products.append(name)
        
        return products
    
    async def get_drug_properties(self, rxcui: str) -> Dict:
        """
        Get detailed properties for a specific drug by RXCUI.
        
        Args:
            rxcui: RxNorm Concept Unique Identifier
        
        Returns:
            Dictionary with drug properties
        """
        url = f"{self.BASE_URL}/rxcui/{rxcui}/properties.json"
        
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Error fetching properties for RXCUI {rxcui}: {e}")
            return {}
    
    async def get_related_drugs(self, rxcui: str) -> List[Dict]:
        """
        Get related drugs (generic, brand equivalents).
        
        Args:
            rxcui: RxNorm Concept Unique Identifier
        
        Returns:
            List of related drugs
        """
        url = f"{self.BASE_URL}/rxcui/{rxcui}/related.json"
        params = {"tty": "SBD+SCD+BN"}
        
        try:
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            related = []
            concept_group = data.get("relatedGroup", {}).get("conceptGroup", [])
            
            for group in concept_group:
                for prop in group.get("conceptProperties", []):
                    related.append({
                        "rxcui": prop.get("rxcui"),
                        "name": prop.get("name"),
                        "tty": prop.get("tty")
                    })
            
            return related
        
        except requests.RequestException as e:
            logger.error(f"Error fetching related drugs: {e}")
            return []
    
    async def search_approximate(self, term: str, max_results: int = 10) -> List[Dict]:
        """
        Approximate search for drug names (useful for autocomplete).
        
        Args:
            term: Search term
            max_results: Maximum number of results
        
        Returns:
            List of matching drugs with RXCUIs
        """
        url = f"{self.BASE_URL}/approximateTerm.json"
        params = {
            "term": term,
            "maxEntries": max_results
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            candidates = data.get("approximateGroup", {}).get("candidate", [])
            
            return [
                {
                    "rxcui": c.get("rxcui"),
                    "name": c.get("name"),
                    "score": c.get("score")
                }
                for c in candidates
            ]
        
        except requests.RequestException as e:
            logger.error(f"Error in approximate search: {e}")
            return []