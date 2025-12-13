"""
Dosage Service - Find appropriate dose for patient
"""
from typing import Dict, Optional, List
from api.dependencies import get_drug_database
from services.openfda_service import OpenFDAService
from utilities.data_parser import DataParser
from services.dosage_calculator import DosageCalculator
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
        age_months: Optional[int] = None,
        dosage_numeric: Optional[float] = None
    ) -> Dict:
        """Get dose recommendation for patient."""
        product = await self._get_product(rxcui)
        chart = self.database.get_dosing_chart(rxcui)
        
        # No chart available
        if not chart:
            return self._build_response(None, product)
        
        # Try to find dose from chart
        dose_result = self._find_dose_from_chart(
            product, chart, weight_lb, age_months, dosage_numeric
        )
        
        # If no match found (outside chart range), recommend doctor consultation
        if not dose_result:
            dose_result = {
                "dose_ml": None,
                "dose_text": "consult a healthcare provider",
                "warning": "Patient parameters outside recommended dosing chart range."
            }
        
        return self._build_response(dose_result, product)
    
    # ==================== DATA FETCHING ====================
    
    async def _get_product(self, rxcui: str) -> Dict:
        """Get product, fetching if not cached."""
        product = self.database.get_product(rxcui)
        
        if not product or not product.get("purpose"):
            await self._fetch_and_save(rxcui)
            product = self.database.get_product(rxcui)
        
        return product
    
    async def _fetch_and_save(self, rxcui: str):
        print(f"🔍 Fetching FDA data for rxcui: {rxcui}")
        try:
            raw_fda = await self.openfda.get_drug_info(rxcui)
            
            if raw_fda:
                print(f"✅ Got FDA data, parsing...")
                cleaned = self.parser.parse_fda_label(raw_fda)
                print(f"✅ Parsed data: {list(cleaned.keys())}")
                
                self.database.save_fda_info(rxcui, cleaned)
                print(f"✅ Saved FDA data to database")
            else:
                print(f"❌ No FDA data found for rxcui: {rxcui}")
                logger.warning(f"No FDA data found for rxcui: {rxcui}")
        except Exception as e:
            print(f"❌ ERROR fetching/saving FDA data: {e}")
            logger.error(f"Failed to fetch/save FDA data for {rxcui}: {e}")
    
    # ==================== DOSE MATCHING LOGIC ====================
    
    def _find_dose_from_chart(
        self,
        product: Dict,
        chart: List[Dict], 
        weight_lb: Optional[float],
        age_months: Optional[int],
        dosage_numeric: Optional[float]
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
            dose_info = self._format_dose(weight_match)
            return {**dose_info, "warning": None}
        
        # Mismatched - calculate exact dose
        if weight_match and age_match and weight_match != age_match:
            calculated = self._calculate_exact_dose(product, chart, weight_lb, dosage_numeric)
            if calculated:
                return {
                    "dose_ml": calculated,
                    "dose_text": None,
                    "warning": "Weight exceeds typical range for age. Dose calculated. Consult healthcare provider."
                }
        
        # Only weight
        if weight_match:
            dose_info = self._format_dose(weight_match)
            return {**dose_info, "warning": None}
        
        # Only age
        if age_match:
            dose_info = self._format_dose(age_match)
            return {
                **dose_info, 
                "warning": "Age-based dosing less accurate than weight-based."
            }
        
        # No match found - return None (handled in get_dose)
        return None
    
    def _calculate_exact_dose(
        self,
        product: Dict,
        chart: List[Dict],
        weight_lb: float,
        dosage_numeric: Optional[float] = None
    ) -> Optional[str]:
        """Calculate exact dose using mg/kg from chart."""
        try:
            concentration = dosage_numeric
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
    
    def _format_dose(self, row: Dict) -> Dict:
        """Extract dose information from chart row."""
        dose_ml = row.get("dose_ml")
        dose_text = row.get("dose_text")
        
        # Format dose_ml if it exists
        if dose_ml is not None:
            return {
                "dose_ml": f"{dose_ml} mL",
                "dose_text": None
            }
        
        # Otherwise return text instruction
        return {
            "dose_ml": None,
            "dose_text": dose_text or "ask a doctor"
        }
    
    # ==================== RESPONSE BUILDING ====================
    
    def _build_response(
        self,
        dose_result: Optional[Dict],
        product: Dict
    ) -> Dict:
        """Build user-facing response."""
        response = {
            "purpose": product.get("purpose", ""),
            "dose_ml": dose_result.get("dose_ml") if dose_result else None,
            "dose_text": dose_result.get("dose_text") if dose_result else None,
            "instructions": product.get("dosage_instructions", ""),
            "warnings": product.get("warnings", ""),
            "contraindications": product.get("contraindications", ""),
            "adverse_reactions": product.get("adverse_reactions", "")
        }
        
        if dose_result and dose_result.get("warning"):
            response["warning"] = dose_result["warning"]
        
        return response