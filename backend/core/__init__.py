"""
Core utilities and configuration
"""
from backend.core.config import settings
from backend.core.exceptions import (
    DrugLookupException,
    DrugNotFoundException,
    OCRProcessingException,
    NERExtractionException,
    DosageCalculationException,
    InvalidInputException,
    APITimeoutException,
    CacheException
)

__all__ = [
    "settings",
    "DrugLookupException",
    "DrugNotFoundException",
    "OCRProcessingException",
    "NERExtractionException",
    "DosageCalculationException",
    "InvalidInputException",
    "APITimeoutException",
    "CacheException"
]