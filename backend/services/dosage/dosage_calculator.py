"""
Dosage Calculator - Pure Pediatric Mathematical Functions
"""

class DosageCalculator:
    """Pure pediatric dosage calculations with validation."""

    STANDARD_ADULT_WEIGHT_KG = 70
    YOUNGS_RULE_CONSTANT = 12

    def clarks_rule(self, adult_dose_mg: float, weight_kg: float) -> float:
        """
        Weight-based pediatric dosing.
        """
        return (weight_kg / self.STANDARD_ADULT_WEIGHT_KG) * adult_dose_mg

    def youngs_rule(self, adult_dose_mg: float, age_years: int) -> float:
        """
        Age-based pediatric dosing.
        """
        return (age_years / (age_years + self.YOUNGS_RULE_CONSTANT)) * adult_dose_mg

    def frieds_rule(self, adult_dose_mg: float, age_months: int) -> float:
        """
        Infant pediatric dosing (< 2 years).
        """

        if age_months < 0:
            raise ValueError("Age in months cannot be negative")
        if age_months > 24:
            raise ValueError("Fried's rule only for infants under 24 months")
        
        return (age_months / 150) * adult_dose_mg

    def calculate_mg_per_kg(self, dose_per_kg: float, weight_kg: float) -> float:
        """
        Calculate dose from mg/kg instruction.
        Example: 10mg/kg for 50kg = 500mg
        """
        if dose_per_kg <= 0:
            raise ValueError("Dose per kg must be positive")
        
        self._validate_weight(weight_kg)
        
        return dose_per_kg * weight_kg

    def convert_dose_units(self, dose_mg: float, target_unit: str) -> float:
        """
        Convert dose to different units.
        Supported: mg, mcg, g
        """
        conversions = {
            "mg": dose_mg,
            "mcg": dose_mg * 1000,
            "g": dose_mg / 1000
        }
        
        unit_lower = target_unit.lower()
        if unit_lower not in conversions:
            raise ValueError(f"Unsupported unit: {target_unit}")
        
        return conversions[unit_lower]

    def _validate_weight(self, weight_kg: float):
        """Validate weight is reasonable."""
        if weight_kg < 2.5:
            raise ValueError("Weight must be greater than 2.5kg")
        if weight_kg > 200:
            raise ValueError("Weight must be ≤ 200kg")

    