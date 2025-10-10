import json
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default cache file path
CACHE_FILE = "data/cached_labels.json"
MISMATCH_LOG_FILE = "data/mismatches.log"

def ensure_data_directory():
    """Ensure the data directory exists."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

def load_cached_labels() -> Dict[str, List[str]]:
    """
    Load cached drug labels from JSON file.
    
    Returns:
        Dictionary mapping brand names to product lists
    """
    ensure_data_directory()
    
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Error decoding {CACHE_FILE}, returning empty cache")
        return {}
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
        return {}

def save_cached_labels(labels: Dict[str, List[str]]) -> bool:
    """
    Save drug labels to cache file.
    
    Args:
        labels: Dictionary of brand names to product lists
    
    Returns:
        True if successful, False otherwise
    """
    ensure_data_directory()
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(labels, f, indent=2, ensure_ascii=False)
        logger.info(f"Cache saved with {len(labels)} brands")
        return True
    except Exception as e:
        logger.error(f"Error saving cache: {e}")
        return False

def log_mismatch(original: str, corrected: str, confidence: float, source: str = "unknown"):
    """
    Log spelling mismatches for analysis and model improvement.
    
    Args:
        original: Original text
        corrected: Corrected text
        confidence: Confidence score
        source: Source of the text (OCR, user_input, etc.)
    """
    ensure_data_directory()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "original": original,
        "corrected": corrected,
        "confidence": confidence,
        "source": source
    }
    
    try:
        with open(MISMATCH_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Error logging mismatch: {e}")

def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the cached data.
    
    Returns:
        Dictionary with cache statistics
    """
    cached_labels = load_cached_labels()
    
    if not cached_labels:
        return {
            "total_brands": 0,
            "total_products": 0,
            "cache_size_bytes": 0,
            "last_modified": None
        }
    
    total_brands = len(cached_labels)
    total_products = sum(len(products) for products in cached_labels.values())
    
    # Get file size
    cache_size = 0
    if os.path.exists(CACHE_FILE):
        cache_size = os.path.getsize(CACHE_FILE)
    
    # Get last modified time
    last_modified = None
    if os.path.exists(CACHE_FILE):
        timestamp = os.path.getmtime(CACHE_FILE)
        last_modified = datetime.fromtimestamp(timestamp).isoformat()
    
    return {
        "total_brands": total_brands,
        "total_products": total_products,
        "cache_size_bytes": cache_size,
        "cache_size_mb": round(cache_size / (1024 * 1024), 2),
        "last_modified": last_modified
    }

def get_mismatch_analytics() -> Dict[str, Any]:
    """
    Analyze logged mismatches for common patterns.
    
    Returns:
        Analytics about spelling corrections
    """
    ensure_data_directory()
    
    if not os.path.exists(MISMATCH_LOG_FILE):
        return {
            "total_corrections": 0,
            "common_mistakes": [],
            "by_source": {}
        }
    
    mismatches = []
    try:
        with open(MISMATCH_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    mismatches.append(json.loads(line))
    except Exception as e:
        logger.error(f"Error reading mismatch log: {e}")
        return {"error": str(e)}
    
    # Count by mistake pattern
    mistake_counts = {}
    source_counts = {}
    
    for entry in mismatches:
        pair = f"{entry['original']} → {entry['corrected']}"
        mistake_counts[pair] = mistake_counts.get(pair, 0) + 1
        
        source = entry.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Sort by frequency
    common_mistakes = sorted(
        mistake_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    return {
        "total_corrections": len(mismatches),
        "common_mistakes": [{"pattern": k, "count": v} for k, v in common_mistakes],
        "by_source": source_counts,
        "unique_patterns": len(mistake_counts)
    }

def clear_cache() -> bool:
    """Clear the cached labels."""
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        logger.info("Cache cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False