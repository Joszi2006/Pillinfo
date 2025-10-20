"""
Dosage Calculator Service
Single Responsibility: Pediatric dosage calculations only
"""

from typing import Dict, Optional
import math


class DosageCalculator:
    """
    Calculates pediatric dosages using standard formulas.

    DISCLAIMER: These are estimates for educational purposes.
    Always consult healthcare professionals for actual dosing.
    """

    STANDARD_ADULT_WEIGHT_KG = 70
    YOUNGS_RULE_CONSTANT = 12
    MIN_WEIGHT_KG = 2.5
    MAX_WEIGHT_KG = 200
    MIN_AGE = 0
    MAX_AGE = 18

    # MAIN ENTRY FUNCTION
   

    def calculate_pediatric_dosage(
        self,
        adult_dose_mg: float,
        patient_weight_kg: float,
        patient_age: Optional[int] = None
    ) -> Dict:
        """Main entry point for all pediatric dosage calculations."""
        self._validate_inputs(adult_dose_mg, patient_weight_kg, patient_age)

        methods = self._calculate_methods(adult_dose_mg, patient_weight_kg, patient_age)
        recommended_dose = methods["clarks_rule"]["dose_mg"]

        warnings = self._generate_warnings(recommended_dose, patient_weight_kg, patient_age)

        return {
            "adult_dose_mg": adult_dose_mg,
            "patient_weight_kg": patient_weight_kg,
            "patient_age": patient_age,
            "methods": methods,
            "recommended_dose_mg": recommended_dose,
            "warnings": warnings
        }

    # HELPER GROUP : CALCULATION METHODS
    

    def _calculate_methods(
        self, adult_dose_mg: float, weight_kg: float, age: Optional[int]
    ) -> Dict[str, Dict]:
        """Run all applicable pediatric dose formulas."""
        methods = {}

        # Clark’s Rule (weight-based)
        clarks = self._clarks_rule(adult_dose_mg, weight_kg)
        methods["clarks_rule"] = self._build_method_result(
            dose=clarks,
            description="Weight-based calculation",
            formula=f"({weight_kg} kg / {self.STANDARD_ADULT_WEIGHT_KG} kg) × {adult_dose_mg} mg"
        )

        # Young’s Rule (if age provided)
        if age is not None and age <= self.MAX_AGE:
            youngs = self._youngs_rule(adult_dose_mg, age)
            methods["youngs_rule"] = self._build_method_result(
                dose=youngs,
                description="Age-based calculation",
                formula=f"({age} / ({age} + {self.YOUNGS_RULE_CONSTANT})) × {adult_dose_mg} mg"
            )

        # Fried’s Rule (for infants < 2 years)
        if age is not None and age < 2:
            months = age * 12
            frieds = self._frieds_rule(adult_dose_mg, months)
            methods["frieds_rule"] = self._build_method_result(
                dose=frieds,
                description="Infant calculation (< 2 years)",
                formula=f"({months} months / 150) × {adult_dose_mg} mg"
            )

        return methods

    def _build_method_result(self, dose: float, description: str, formula: str) -> Dict:
        """Format a single rule’s calculation result."""
        return {
            "dose_mg": round(dose, 2),
            "description": description,
            "formula": formula
        }

    
    # HELPER GROUP : FORMULAS
  

    def _clarks_rule(self, adult_dose_mg: float, weight_kg: float) -> float:
        return (weight_kg / self.STANDARD_ADULT_WEIGHT_KG) * adult_dose_mg

    def _youngs_rule(self, adult_dose_mg: float, age_years: int) -> float:
        return (age_years / (age_years + self.YOUNGS_RULE_CONSTANT)) * adult_dose_mg

    def _frieds_rule(self, adult_dose_mg: float, age_months: float) -> float:
        return (age_months / 150) * adult_dose_mg

    # ----------------------------
    # HELPER GROUP 3: VALIDATION
    # ----------------------------

    def _validate_inputs(
        self, adult_dose_mg: float, weight_kg: float, age: Optional[int]
    ):
        if adult_dose_mg <= 0:
            raise ValueError("Adult dose must be positive.")
        if weight_kg < self.MIN_WEIGHT_KG:
            raise ValueError(f"Weight must be ≥ {self.MIN_WEIGHT_KG} kg.")
        if weight_kg > self.MAX_WEIGHT_KG:
            raise ValueError(f"Weight seems unreasonably high ({weight_kg} kg).")
        if age is not None:
            if age < self.MIN_AGE:
                raise ValueError("Age cannot be negative.")
            if age > 120:
                raise ValueError("Age seems unreasonably high.")

    # ----------------------------
    # HELPER GROUP 4: WARNINGS
    # ----------------------------

    def _generate_warnings(
        self, dose: float, weight_kg: float, age: Optional[int]
    ) -> list:
        warnings = [
            "⚠️ CRITICAL: Calculations are estimates only. Consult a healthcare provider before administering any medication."
        ]

        if weight_kg < 10:
            warnings.append("⚠️ Very low weight detected. Infant dosing requires specialist input.")
        if age is not None:
            if age < 2:
                warnings.append("⚠️ Patient is an infant (< 2 years). Use Fried’s Rule and consult a pediatrician.")
            elif age >= 12:
                warnings.append("⚠️ Patient is approaching adult age. Consider adult dosing or confirm with physician.")
        if dose < 1:
            warnings.append("⚠️ Calculated dose is very small. Verify with a pharmacist for accuracy.")

        return warnings

    # ----------------------------
    # HELPER GROUP 5: UTILITY FUNCTIONS
    # ----------------------------

    def convert_dose_units(self, dose_mg: float, target_unit: str) -> Dict:
        conversions = {"mcg": dose_mg * 1000, "g": dose_mg / 1000, "mg": dose_mg}
        if target_unit.lower() not in conversions:
            raise ValueError(f"Unsupported unit: {target_unit}")
        return {
            "original_mg": dose_mg,
            "converted_value": round(conversions[target_unit.lower()], 4),
            "unit": target_unit
        }

    def dose_by_body_surface_area(self, adult_dose_mg: float, height_cm: float, weight_kg: float) -> Dict:
        bsa = math.sqrt((height_cm * weight_kg) / 3600)
        adult_bsa = 1.73
        pediatric_dose = (bsa / adult_bsa) * adult_dose_mg
        return {
            "method": "Body Surface Area (BSA)",
            "bsa_m2": round(bsa, 3),
            "adult_bsa_m2": adult_bsa,
            "dose_mg": round(pediatric_dose, 2),
            "description": "Most accurate for chemotherapy and critical care",
            "formula": f"({bsa} m² / {adult_bsa} m²) × {adult_dose_mg} mg"
        }
