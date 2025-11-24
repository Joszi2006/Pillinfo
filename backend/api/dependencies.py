"""
Dependency Injection - Singleton Management
"""
from functools import lru_cache
import os
from anthropic import Anthropic
from backend.ml.ner_extractor import NERExtractor
from backend.services.drug_database import DrugDatabase


# ==================== SINGLETONS ====================

@lru_cache()
def get_claude_client() -> Anthropic:
    """Claude API client singleton."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    return Anthropic(api_key=api_key)


@lru_cache()
def get_ner_extractor():
    """NER model singleton (loads GLiNER once)."""
    return NERExtractor()


@lru_cache()
def get_drug_database():
    """Database connection singleton."""
    return DrugDatabase()