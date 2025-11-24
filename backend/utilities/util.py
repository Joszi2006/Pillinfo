"""
Utilities - Logging for training data
"""
import json
import os
from datetime import datetime
from typing import Dict, Any

DATA_DIR = "data"
MISMATCH_LOG_FILE = "data/mismatches.log"
EXTRACTION_LOG_FILE = "data/training_data/successful_extractions.log"


def ensure_data_directory():
    """Ensure data directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs("data/training_data", exist_ok=True)


def log_mismatch(original: str, corrected: str, confidence: float, source: str = "unknown"):
    """Log spelling mismatches for model improvement."""
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
        print(f"Error logging mismatch: {e}")


def log_successful_extraction(
    text: str,
    brand_name: str,
    dosage: str = None,
    route: str = None,
    form: str = None,
    confidence: float = 0
):
    """Log successful extractions for training."""
    ensure_data_directory()
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "extracted_drug": brand_name,
        "dosage": dosage,
        "route": route,
        "form": form,
        "correction_confidence": confidence
    }
    
    try:
        with open(EXTRACTION_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Error logging extraction: {e}")


def get_mismatch_analytics() -> Dict[str, Any]:
    """Analyze logged mismatches for patterns."""
    if not os.path.exists(MISMATCH_LOG_FILE):
        return {"total_corrections": 0, "common_mistakes": []}
    
    mismatches = []
    try:
        with open(MISMATCH_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    mismatches.append(json.loads(line))
    except Exception as e:
        return {"error": str(e)}
    
    # Count patterns
    mistake_counts = {}
    for entry in mismatches:
        pair = f"{entry['original']} → {entry['corrected']}"
        mistake_counts[pair] = mistake_counts.get(pair, 0) + 1
    
    common = sorted(mistake_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_corrections": len(mismatches),
        "common_mistakes": [{"pattern": k, "count": v} for k, v in common]
    }