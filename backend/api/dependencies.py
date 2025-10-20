"""
Dependency Injection
Single Responsibility: Provide dependency instances
"""
from backend.services.drug_lookup_service import DrugLookupService
from backend.utilities.dosage_calculator import DosageCalculator
from backend.services.cache_service import CacheService
from backend.services.rxnorm_service import RxNormService
from backend.services.ocr_service import OCRService
from backend.ml.ner_extractor import NERExtractor
from backend.ml.fuzzy_matcher import FuzzyMatcher

# Service singletons (created once, reused)
_drug_lookup_service = None
_dosage_calculator = None
_cache_service = None
_rxnorm_service = None
_ocr_service = None
_ner_extractor = None
_fuzzy_matcher = None

def get_drug_lookup_service() -> DrugLookupService:
    """Get or create DrugLookupService instance."""
    global _drug_lookup_service
    if _drug_lookup_service is None:
        _drug_lookup_service = DrugLookupService()
    return _drug_lookup_service

def get_dosage_calculator() -> DosageCalculator:
    """Get or create DosageCalculator instance."""
    global _dosage_calculator
    if _dosage_calculator is None:
        _dosage_calculator = DosageCalculator()
    return _dosage_calculator

def get_cache_service() -> CacheService:
    """Get or create CacheService instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

def get_rxnorm_service() -> RxNormService:
    """Get or create RxNormService instance."""
    global _rxnorm_service
    if _rxnorm_service is None:
        _rxnorm_service = RxNormService()
    return _rxnorm_service

def get_ocr_service() -> OCRService:
    """Get or create OCRService instance."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service

def get_ner_extractor() -> NERExtractor:
    """Get or create NERExtractor instance."""
    global _ner_extractor
    if _ner_extractor is None:
        _ner_extractor = NERExtractor()
    return _ner_extractor

def get_fuzzy_matcher() -> FuzzyMatcher:
    """Get or create FuzzyMatcher instance."""
    global _fuzzy_matcher
    if _fuzzy_matcher is None:
        _fuzzy_matcher = FuzzyMatcher()
        # Inject cache into fuzzy matcher
        cache_service = get_cache_service()
        _fuzzy_matcher.set_cache(cache_service.get_cache_dict())
    return _fuzzy_matcher