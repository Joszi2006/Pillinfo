"""
Configuration Management
Single Responsibility: Centralize all configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
# import os

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # API Configuration
    API_TITLE: str = "Drug Lookup API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Multi-modal drug information lookup with OCR and NLP"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # RxNorm API
    RXNORM_BASE_URL: str = "https://rxnav.nlm.nih.gov/REST"
    RXNORM_TIMEOUT: int = 5
    
    # Cache Configuration
    CACHE_FILE: str = "data/cached_labels.json"
    MISMATCH_LOG_FILE: str = "data/mismatches.log"
    
    # ML Configuration
    MEDSPACY_MODEL: Optional[str] = None  # If None, uses default
    FUZZY_MATCH_THRESHOLD: int = 85
    
    # OCR Configuration
    TESSERACT_PATH: Optional[str] = None  # Auto-detect if None
    OCR_PREPROCESSING: bool = True
    
    # Dosage Calculator Configuration
    STANDARD_ADULT_WEIGHT_KG: float = 70.0
    YOUNGS_RULE_CONSTANT: int = 12
    
    # File Upload Limits
    MAX_IMAGE_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/jpg"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Common drugs for cache seeding
COMMON_DRUGS = [
    # Cardiovascular
    "Lipitor", "Crestor", "Plavix", "Lisinopril", "Atorvastatin",
    "Metoprolol", "Amlodipine", "Losartan", "Warfarin",
    
    # Diabetes
    "Metformin", "Lantus", "Humalog", "Januvia", "Glipizide",
    
    # Pain/Inflammation
    "Advil", "Tylenol", "Aspirin", "Ibuprofen", "Naproxen",
    "Celebrex", "Tramadol",
    
    # Respiratory
    "Ventolin", "Advair", "Singulair", "Symbicort", "Albuterol",
    
    # GI
    "Nexium", "Prilosec", "Zantac", "Omeprazole",
    
    # Mental Health
    "Zoloft", "Prozac", "Lexapro", "Xanax", "Abilify",
    
    # Antibiotics
    "Amoxicillin", "Azithromycin", "Cipro", "Doxycycline"
]

# Route normalization mappings
ROUTE_ALIASES = {
    "orally": "oral",
    "po": "oral",
    "by mouth": "oral",
    "iv": "intravenous",
    "intravenously": "intravenous",
    "im": "intramuscular",
    "intramuscularly": "intramuscular",
    "sq": "subcutaneous",
    "subq": "subcutaneous",
    "subcutaneously": "subcutaneous",
    "topically": "topical",
    "apply": "topical",
    "transdermally": "transdermal",
}

# Medical disclaimer
MEDICAL_DISCLAIMER = """
⚠️⚠️⚠️ CRITICAL MEDICAL DISCLAIMER ⚠️⚠️⚠️

This system is for EDUCATIONAL and INFORMATIONAL purposes only.

DO NOT use these dosage calculations for actual medical treatment.

Pediatric dosing requires:
- Licensed healthcare provider evaluation
- Complete medical history review
- Consideration of drug interactions
- Monitoring for adverse effects
- Adjustment based on response

ALWAYS consult a pediatrician, pharmacist, or licensed 
healthcare provider before administering ANY medication to a child.

Improper dosing can cause serious harm or death.
"""