"""
Custom Exceptions
Single Responsibility: Define application-specific exceptions
"""

class DrugLookupException(Exception):
    """Base exception for drug lookup operations."""
    pass

class DrugNotFoundException(DrugLookupException):
    """Raised when drug is not found in cache or API."""
    def __init__(self, drug_name: str):
        self.drug_name = drug_name
        super().__init__(f"Drug not found: {drug_name}")

class OCRProcessingException(DrugLookupException):
    """Raised when OCR processing fails."""
    pass

class NERExtractionException(DrugLookupException):
    """Raised when NER extraction fails."""
    pass

class DosageCalculationException(DrugLookupException):
    """Raised when dosage calculation fails."""
    pass

class InvalidInputException(DrugLookupException):
    """Raised when user input is invalid."""
    pass

class APITimeoutException(DrugLookupException):
    """Raised when external API times out."""
    def __init__(self, api_name: str, timeout: int):
        self.api_name = api_name
        self.timeout = timeout
        super().__init__(f"{api_name} timed out after {timeout}s")

class CacheException(DrugLookupException):
    """Raised when cache operations fail."""
    pass