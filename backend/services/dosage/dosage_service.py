"""
Dosage Service - Find appropriate dose for patient
"""
from typing import Dict, Optional, List
from backend.api.dependencies import get_drug_database
from backend.services.dosage.openfda_service import OpenFDAService
from backend.services.dosage.data_parser import DataParser
from backend.services.dosage.dosage_calculator import DosageCalculator
import logging

logger = logging.getLogger(__name__)


class DosageService:
    """Find dose for patient from FDA dosing charts."""
    
    def __init__(self):
        self.database = get_drug_database()
        self.openfda = OpenFDAService()
        self.parser = DataParser()
        self.calculator = DosageCalculator()
    
    # ==================== PUBLIC API ====================
    
    async def get_dose(
        self, 
        rxcui: str, 
        weight_lb: Optional[float] = None,
        age_months: Optional[int] = None
    ) -> Dict:
        """Get dose recommendation for patient."""
        product = await self._get_product(rxcui)
        chart = self.database.get_dosing_chart(rxcui)
        
        if not chart:
            return self._build_response(None, product)
        
        dose_result = self._find_dose_from_chart(
            product, chart, weight_lb, age_months
        )
        
        if dose_result:
            return self._build_response(
                dose_result["dose"],
                product,
                dose_result.get("warning")
            )
        
        return self._build_response("ask a doctor", product)
    
    # ==================== DATA FETCHING ====================
    
    async def _get_product(self, rxcui: str) -> Dict:
        """Get product, fetching if not cached."""
        product = self.database.get_product(rxcui)
        
        if not product or not product.get("purpose"):
            await self._fetch_and_save(rxcui)
            product = self.database.get_product(rxcui)
        
        return product
    
    async def _fetch_and_save(self, rxcui: str):
        """Fetch from OpenFDA and save to database."""
        try:
            logger.info(f"Fetching FDA data for rxcui: {rxcui}")
            raw_fda = await self.openfda.get_drug_info(rxcui)
            
            if raw_fda:
                logger.debug(f"Successfully fetched FDA data for {rxcui}")
                cleaned = self.parser.parse_fda_label(raw_fda)
                self.database.save_fda_info(rxcui, cleaned)
            else:
                logger.warning(f"No FDA data found for rxcui: {rxcui}")
        except Exception as e:
            logger.error(f"Failed to fetch/save FDA data for {rxcui}: {e}")
    
    # ==================== DOSE MATCHING LOGIC ====================
    
    def _find_dose_from_chart(
        self,
        product: Dict,
        chart: List[Dict], 
        weight_lb: Optional[float],
        age_months: Optional[int]
    ) -> Optional[Dict]:
        """Find matching dose from chart."""
        weight_match = None
        age_match = None
        
        for row in chart:
            if weight_lb and self._in_range(
                weight_lb, 
                row.get("min_weight_lb"), 
                row.get("max_weight_lb")
            ):
                weight_match = row
            
            if age_months and self._in_range(
                age_months, 
                row.get("min_age_months"), 
                row.get("max_age_months")
            ):
                age_match = row
        
        # Perfect match
        if weight_match and age_match and weight_match == age_match:
            dose = self._format_dose(weight_match)
            return {"dose": dose, "warning": None}
        
        # Mismatched - calculate exact dose
        if weight_match and age_match and weight_match != age_match:
            calculated = self._calculate_exact_dose(product, chart, weight_lb)
            if calculated:
                return {
                    "dose": calculated,
                    "warning": "Weight exceeds typical range for age. Dose calculated. Consult healthcare provider."
                }
        
        # Only weight
        if weight_match:
            dose = self._format_dose(weight_match)
            return {"dose": dose, "warning": None}
        
        # Only age
        if age_match:
            dose = self._format_dose(age_match)
            return {
                "dose": dose,
                "warning": "Age-based dosing less accurate than weight-based."
            }
        
        return None
    
    def _calculate_exact_dose(
        self,
        product: Dict,
        chart: List[Dict],
        weight_lb: float
    ) -> Optional[str]:
        """Calculate exact dose using mg/kg from chart."""
        try:
            concentration = self.parser.extract_concentration(
                product.get("product_name", "")
            )
            if not concentration:
                return None
            
            mg_per_kg = self.calculator.extract_mg_per_kg_from_chart(
                chart, concentration
            )
            dose_ml = self.calculator.calculate_dose_from_weight(
                weight_lb, mg_per_kg, concentration
            )
            
            return f"{dose_ml} mL" if dose_ml else None
        except Exception as e:
            logger.error(f"Error calculating exact dose: {e}")
            return None
    
    # ==================== UTILITIES ====================
    
    def _in_range(self, value: float, min_val, max_val) -> bool:
        """Check if value falls in range."""
        if min_val is None and max_val is None:
            return False
        if min_val is None:
            return value <= max_val
        if max_val is None:
            return value >= min_val
        return min_val <= value <= max_val
    
    def _format_dose(self, row: Dict) -> str:
        """Format dose from chart row."""
        if row.get("dose_ml"):
            return f"{row['dose_ml']} mL"
        return row.get("dose_text", "ask a doctor")
    
    # ==================== RESPONSE BUILDING ====================
    
    def _build_response(
        self,
        dose: Optional[str],
        product: Dict,
        warning: Optional[str] = None
    ) -> Dict:
        """Build user-facing response."""
        response = {
            "dose": dose,
            "instructions": product.get("dosage_instructions", ""),
            "warnings": product.get("warnings", ""),
            "contraindications": product.get("contraindications", ""),
            "adverse_reactions": product.get("adverse_reactions", "")
        }
        if warning:
            response["warning"] = warning
        return response