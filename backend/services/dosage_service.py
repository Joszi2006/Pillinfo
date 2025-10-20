"""
Hybrid Dosage Service - Combines OpenFDA + Calculator 
"""

import re
from typing import Dict, Optional
from backend.services.openfda_service import OpenFDAService
from backend.utilities.dosage_calculator import DosageCalculator


class DosageService:
    """Provides safest available dosage information."""

    RESTRICTION_PATTERNS = [
        r"not recommended",
        r"do not use",
        r"contraindicated",
        r"consult a doctor",
        r"children under\s*\d+",
        r"infants under\s*\d+",
    ]

    WEIGHT_BASED_PATTERN = r"(mg/kg|ml/kg|per\s*kg|mcg/kg)"

    def __init__(
        self,
        openfda_service: Optional[OpenFDAService] = None,
        dosage_calculator: Optional[DosageCalculator] = None,
    ):
        self.openfda_service = openfda_service or OpenFDAService()
        self.dosage_calculator = dosage_calculator or DosageCalculator()

    # ---------- Helper Functions ---------- #

    def _is_restricted(self, text: str) -> bool:
        """Check if text mentions pediatric restriction."""
        return any(re.search(pat, text, re.IGNORECASE) for pat in self.RESTRICTION_PATTERNS)

    def _is_weight_based(self, text: str) -> bool:
        """Check if dosage mentions mg/kg etc."""
        return bool(re.search(self.WEIGHT_BASED_PATTERN, text, re.IGNORECASE))

    def _build_restricted_response(self, fda_info, dosage_text, pediatric_text) -> Dict:
        """Return structured restricted result."""
        return {
            "source": "fda_official",
            "confidence": "high",
            "dosing_info": {
                "dosage_and_administration": dosage_text,
                "pediatric_use": pediatric_text,
                "warnings": fda_info.get("warnings"),
                "contraindications": fda_info.get("contraindications"),
            },
            "note": "Restricted pediatric use. Consult healthcare provider.",
            "warnings": [
                {
                    "level": "critical",
                    "category": "restriction_detected",
                    "message": "FDA label indicates this product is not safe for some ages.",
                }
            ],
        }

    def _build_fda_response(self, fda_info, dosage_text, pediatric_text, weight_based) -> Dict:
        """Return structured FDA-based result."""
        return {
            "source": "fda_official",
            "confidence": "high",
            "dosing_info": {
                "dosage_and_administration": dosage_text,
                "pediatric_use": pediatric_text,
                "weight_based": weight_based,
                "warnings": fda_info.get("warnings"),
                "contraindications": fda_info.get("contraindications"),
            },
            "note": "Official FDA-approved pediatric dosing.",
            "warnings": [
                {
                    "level": "info",
                    "category": "source_info",
                    "message": "Information retrieved from official FDA drug label.",
                }
            ],
        }

    def _build_calculated_response(self, calculated: Dict) -> Dict:
        """Return structured calculated fallback."""
        warnings = calculated.get("warnings", [])
        warnings.insert(0, {
            "level": "critical",
            "category": "calculation_warning",
            "message": (
                "Calculated using generic formulas, not official guidelines. "
                "Consult healthcare provider."
            ),
        })
        return {
            "source": "calculated_estimate",
            "confidence": "low",
            "dosing_info": calculated,
            "note": "Estimated using pediatric formula.",
            "warnings": warnings,
        }

    def _build_unavailable_response(self) -> Dict:
        """Return structured unavailable response."""
        return {
            "source": "unavailable",
            "confidence": "none",
            "dosing_info": None,
            "note": "No FDA or calculated dosage available. Consult provider.",
            "warnings": [
                {
                    "level": "critical",
                    "category": "no_data",
                    "message": "No pediatric dosing information available.",
                }
            ],
        }

    # ---------- Main Logic ---------- #

    async def get_dosage_info(
        self,
        drug_name: str,
        generic_name: str,
        adult_dose_mg: Optional[float] = None,
        patient_weight_kg: Optional[float] = None,
        patient_age: Optional[int] = None,
        patient_age_months: Optional[int] = None,
    ) -> Dict:
        """Get safest available dosage info."""

        base_result = {
            "patient_weight_kg": patient_weight_kg,
            "patient_age": patient_age,
            "patient_age_months": patient_age_months,
        }

        # --- Step 1: Try FDA data ---
        fda_info = await self.openfda_service.get_drug_info(drug_name, generic_name)
        dosage_field = fda_info.get("dosage_and_administration", "")
        pediatric_field = fda_info.get("pediatric_use", "")
        if fda_info and dosage_field:
            if isinstance(dosage_field, list):
                dosage_text = " ".join(str(v) for v in dosage_field)
            else:
                dosage_text = str(dosage_field)
            if isinstance(pediatric_field, list):
                pediatric_text = " ".join(str(v) for v in pediatric_field)
            else:
                pediatric_text = str(pediatric_field)
            full_text = f"{dosage_text} {pediatric_text}"

            if self._is_restricted(full_text):
                return {**base_result, **self._build_restricted_response(fda_info, dosage_text, pediatric_text)}

            weight_based = self._is_weight_based(dosage_text)
            return {**base_result, **self._build_fda_response(fda_info, dosage_text, pediatric_text, weight_based)}

        # --- Step 2: Fallback to calculator ---
        if adult_dose_mg:
            try:
                calculated = self.dosage_calculator.calculate_pediatric_dosage(
                    adult_dose_mg, patient_weight_kg, patient_age
                )
                return {**base_result, **self._build_calculated_response(calculated)}
            except ValueError as e:
                base_result["calculation_error"] = str(e)

        # --- Step 3: No info available ---
        return {**base_result, **self._build_unavailable_response()}
