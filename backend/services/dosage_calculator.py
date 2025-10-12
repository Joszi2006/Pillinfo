"""
Dosage Calculator Service
Single Responsibility: Pediatric dosage calculations only
"""
from typing import Dict, Optional

class DosageCalculator:
    """
    Calculates pediatric dosages using standard formulas.
    
    DISCLAIMER: These are estimates for educational purposes.
    Always consult healthcare professionals for actual dosing.
    """
    
    # Standard adult weight in kg for calculations
    STANDARD_ADULT_WEIGHT_KG = 70
    
    # Age-based dosing constants
    YOUNGS_RULE_CONSTANT = 12
    
    # Safety limits
    MIN_WEIGHT_KG = 2.5  # Newborn minimum
    MAX_WEIGHT_KG = 200  # Reasonable maximum
    MIN_AGE = 0
    MAX_AGE = 18  # Pediatric cutoff
    
    def calculate_pediatric_dosage(
        self,
        adult_dose_mg: float,
        patient_weight_kg: float,
        patient_age: Optional[int] = None
    ) -> Dict:
        """
        Calculate pediatric dosage using multiple methods.
        
        Args:
            adult_dose_mg: Standard adult dose in milligrams
            patient_weight_kg: Patient's weight in kilograms
            patient_age: Patient's age in years (optional)
        
        Returns:
            Dictionary with calculated dosages and warnings
        
        Raises:
            ValueError: If inputs are invalid
        """
        # Validation
        self._validate_inputs(adult_dose_mg, patient_weight_kg, patient_age)
        
        result = {
            "adult_dose_mg": adult_dose_mg,
            "patient_weight_kg": patient_weight_kg,
            "patient_age": patient_age,
            "methods": {}
        }
        
        # Clark's Rule (weight-based)
        clarks_dose = self._clarks_rule(adult_dose_mg, patient_weight_kg)
        result["methods"]["clarks_rule"] = {
            "dose_mg": round(clarks_dose, 2),
            "description": "Weight-based calculation",
            "formula": f"({patient_weight_kg} kg / {self.STANDARD_ADULT_WEIGHT_KG} kg) × {adult_dose_mg} mg"
        }
        
        # Young's Rule (age-based, if age provided)
        if patient_age is not None and patient_age <= self.MAX_AGE:
            youngs_dose = self._youngs_rule(adult_dose_mg, patient_age)
            result["methods"]["youngs_rule"] = {
                "dose_mg": round(youngs_dose, 2),
                "description": "Age-based calculation",
                "formula": f"({patient_age} / ({patient_age} + {self.YOUNGS_RULE_CONSTANT})) × {adult_dose_mg} mg"
            }
        
        # Fried's Rule (for infants, if age < 2)
        if patient_age is not None and patient_age < 2:
            age_months = patient_age * 12
            frieds_dose = self._frieds_rule(adult_dose_mg, age_months)
            result["methods"]["frieds_rule"] = {
                "dose_mg": round(frieds_dose, 2),
                "description": "Infant calculation (< 2 years)",
                "formula": f"({age_months} months / 150) × {adult_dose_mg} mg"
            }
        
        # Recommended dose (Clark's Rule is most reliable)
        result["recommended_dose_mg"] = round(clarks_dose, 2)
        
        # Safety warnings
        result["warnings"] = self._generate_warnings(
            clarks_dose, 
            patient_weight_kg, 
            patient_age
        )
        
        return result
    
    def _clarks_rule(self, adult_dose_mg: float, patient_weight_kg: float) -> float:
        """
        Clark's Rule: (Weight in kg / 70 kg) × Adult Dose
        Most widely used weight-based calculation.
        """
        return (patient_weight_kg / self.STANDARD_ADULT_WEIGHT_KG) * adult_dose_mg
    
    def _youngs_rule(self, adult_dose_mg: float, age_years: int) -> float:
        """
        Young's Rule: (Age / (Age + 12)) × Adult Dose
        Age-based calculation for children.
        """
        return (age_years / (age_years + self.YOUNGS_RULE_CONSTANT)) * adult_dose_mg
    
    def _frieds_rule(self, adult_dose_mg: float, age_months: float) -> float:
        """
        Fried's Rule: (Age in months / 150) × Adult Dose
        Specifically for infants under 2 years.
        """
        return (age_months / 150) * adult_dose_mg
    
    def _validate_inputs(
        self, 
        adult_dose_mg: float, 
        patient_weight_kg: float, 
        patient_age: Optional[int]
    ):
        """Validate all inputs."""
        if adult_dose_mg <= 0:
            raise ValueError("Adult dose must be positive")
        
        if patient_weight_kg < self.MIN_WEIGHT_KG:
            raise ValueError(f"Weight must be at least {self.MIN_WEIGHT_KG} kg")
        
        if patient_weight_kg > self.MAX_WEIGHT_KG:
            raise ValueError(f"Weight seems unreasonably high: {patient_weight_kg} kg")
        
        if patient_age is not None:
            if patient_age < self.MIN_AGE:
                raise ValueError("Age cannot be negative")
            if patient_age > 120:
                raise ValueError("Age seems unreasonably high")
    
    def _generate_warnings(
        self, 
        calculated_dose: float, 
        weight_kg: float, 
        age: Optional[int]
    ) -> list:
        """Generate appropriate safety warnings."""
        warnings = []
        
        # Universal warning
        warnings.append(
            "⚠️ CRITICAL: These calculations are estimates only. "
            "Always consult a licensed healthcare provider before administering "
            "any medication to a child."
        )
        
        # Low weight warning
        if weight_kg < 10:
            warnings.append(
                "⚠️ Very low weight detected. Infant dosing requires specialist consultation."
            )
        
        # Age-specific warnings
        if age is not None:
            if age < 2:
                warnings.append(
                    "⚠️ Patient is an infant (< 2 years). Use Fried's Rule and consult pediatrician."
                )
            elif age >= 12:
                warnings.append(
                    "⚠️ Patient is approaching adult age. Consider adult dosing or consult doctor."
                )
        
        # Very small dose warning
        if calculated_dose < 1:
            warnings.append(
                "⚠️ Calculated dose is very small. Verify with pharmacist for accurate measurement."
            )
        
        return warnings
    
    def convert_dose_units(
        self, 
        dose_mg: float, 
        target_unit: str
    ) -> Dict:
        """
        Convert dosage to different units.
        
        Args:
            dose_mg: Dose in milligrams
            target_unit: Target unit (mcg, g, ml)
        
        Returns:
            Dictionary with converted value
        """
        conversions = {
            "mcg": dose_mg * 1000,  # mg to mcg
            "g": dose_mg / 1000,     # mg to g
            "mg": dose_mg            # mg to mg (no conversion)
        }
        
        if target_unit.lower() not in conversions:
            raise ValueError(f"Unsupported unit: {target_unit}")
        
        return {
            "original_mg": dose_mg,
            "converted_value": round(conversions[target_unit.lower()], 4),
            "unit": target_unit
        }
    
    def dose_by_body_surface_area(
        self,
        adult_dose_mg: float,
        height_cm: float,
        weight_kg: float
    ) -> Dict:
        """
        Calculate dose using Body Surface Area (BSA) - Most accurate method.
        Uses Mosteller formula: BSA = √((height_cm × weight_kg) / 3600)
        
        Args:
            adult_dose_mg: Adult dose in mg
            height_cm: Patient height in centimeters
            weight_kg: Patient weight in kilograms
        
        Returns:
            Dictionary with BSA-based dosage
        """
        import math
        
        # Calculate BSA
        bsa = math.sqrt((height_cm * weight_kg) / 3600)
        
        # Adult BSA is typically 1.73 m²
        adult_bsa = 1.73
        
        # Calculate pediatric dose
        pediatric_dose = (bsa / adult_bsa) * adult_dose_mg
        
        return {
            "method": "Body Surface Area (BSA)",
            "bsa_m2": round(bsa, 3),
            "adult_bsa_m2": adult_bsa,
            "dose_mg": round(pediatric_dose, 2),
            "description": "Most accurate method for chemotherapy and critical care",
            "formula": f"({bsa} m² / {adult_bsa} m²) × {adult_dose_mg} mg"
        }