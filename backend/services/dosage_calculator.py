"""
Dosage Calculator - Pediatric dosing calculations
"""
from typing import List, Dict


class DosageCalculator:
    """Calculate pediatric doses using formulas and mg/kg extraction."""
    
    LBS_TO_KG = 0.453592
    
    def extract_mg_per_kg_from_chart(
        self, 
        chart: List[Dict], 
        concentration_mg_ml: float
    ) -> float:
        """
        Extract average mg/kg from FDA dosing chart.
        """
        mg_per_kg_values = []
        
        for row in chart:
            dose_ml = row.get("dose_ml")
            if not dose_ml:
                continue
            
            # Get midpoint of weight range
            min_w = row.get("min_weight_lb")
            max_w = row.get("max_weight_lb")
            
            if min_w is None or max_w is None:
                continue
            
            midpoint_lb = (min_w + max_w) / 2
            midpoint_kg = midpoint_lb * self.LBS_TO_KG
            
            # Calculate mg and mg/kg
            total_mg = dose_ml * concentration_mg_ml
            mg_per_kg = total_mg / midpoint_kg
            
            mg_per_kg_values.append(mg_per_kg)
        
        if not mg_per_kg_values:
            return 10.0  # Default safe pediatric ibuprofen dose
        
        return sum(mg_per_kg_values) / len(mg_per_kg_values)
    
    def calculate_dose_from_weight(
        self,
        weight_lb: float,
        mg_per_kg: float,
        concentration_mg_ml: float
    ) -> float:
        """
        Calculate dose based on weight and mg/kg ratio.
        Returns dose in mL.
        """
        weight_kg = weight_lb * self.LBS_TO_KG
        dose_mg = weight_kg * mg_per_kg
        dose_ml = dose_mg / concentration_mg_ml
        return round(dose_ml, 2)
    
  