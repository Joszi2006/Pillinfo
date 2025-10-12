import spacy
import medspacy
from medspacy.ner import TargetRule
from rapidfuzz import process, fuzz
from backend.util import load_cached_labels
from typing import List, Dict, Optional
import json
import os

# Load MedSpacy model
nlp = None

def load_nlp_model():
    """Lazy load the NLP model to avoid loading on import."""
    global nlp
    if nlp is None:
        nlp = medspacy.load()
        
        # Add custom entity ruler for common patterns
        if "entity_ruler" not in nlp.pipe_names:
            ruler = nlp.add_pipe("entity_ruler", before="ner")
            
            patterns = [
                # Dosage patterns
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "mg"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "mcg"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "ml"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": "g"}]},
                {"label": "DOSAGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": {"IN": ["unit", "units"]}}]},
                
                # Route patterns
                {"label": "ROUTE", "pattern": [{"LOWER": "oral"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "orally"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "intravenous"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "intravenously"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "topical"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "topically"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "injection"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "subcutaneous"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": "intramuscular"}]},
                {"label": "ROUTE", "pattern": [{"LOWER": {"IN": ["iv", "im", "sq", "po"]}}]},
            ]
            
            ruler.add_patterns(patterns)
    
    return nlp

def fuzzy_correct_drug_name(drug_name: str, threshold: int = 80) -> Dict:
    """
    Correct drug name using fuzzy matching against cached drugs.
    
    Args:
        drug_name: The drug name to correct
        threshold: Minimum similarity score (0-100)
    
    Returns:
        Dictionary with original, corrected name, and confidence
    """
    cached_labels = load_cached_labels()
    
    if not cached_labels:
        return {
            "original": drug_name,
            "corrected": drug_name,
            "confidence": 0,
            "matched": False
        }
    
    # Try exact match first (case-insensitive)
    for cached_drug in cached_labels.keys():
        if cached_drug.lower() == drug_name.lower():
            return {
                "original": drug_name,
                "corrected": cached_drug,
                "confidence": 100,
                "matched": True
            }
    
    # Fuzzy match
    best_match = process.extractOne(
        drug_name,
        cached_labels.keys(),
        scorer=fuzz.WRatio,
        score_cutoff=threshold
    )
    
    if best_match:
        return {
            "original": drug_name,
            "corrected": best_match[0],
            "confidence": best_match[1],
            "matched": True
        }
    
    return {
        "original": drug_name,
        "corrected": drug_name,
        "confidence": 0,
        "matched": False
    }

def extract_drug_info(text: str, correct_spelling: bool = True) -> Dict:
    """
    Extract drug information from text using MedSpacy.
    
    Args:
        text: Input text to analyze
        correct_spelling: Whether to apply fuzzy correction to drug names
    
    Returns:
        Dictionary with extracted entities and corrections
    """
    nlp_model = load_nlp_model()
    doc = nlp_model(text)
    
    # Extract entities
    drugs = []
    dosages = []
    routes = []
    
    for ent in doc.ents:
        if ent.label_ in ["DRUG", "MEDICATION"]:
            drugs.append(ent.text)
        elif ent.label_ == "DOSAGE":
            dosages.append(ent.text)
        elif ent.label_ == "ROUTE":
            routes.append(ent.text)
    
    # Remove duplicates while preserving order
    drugs = list(dict.fromkeys(drugs))
    dosages = list(dict.fromkeys(dosages))
    routes = list(dict.fromkeys(routes))
    
    # Apply fuzzy correction to drug names
    corrected_drugs = []
    if correct_spelling and drugs:
        for drug in drugs:
            correction = fuzzy_correct_drug_name(drug)
            corrected_drugs.append(correction)
    
    return {
        "raw_text": text,
        "drugs": drugs,
        "dosages": dosages,
        "routes": routes,
        "corrected_drugs": corrected_drugs if correct_spelling else None,
        "all_entities": [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]
    }

def extract_from_ocr_result(ocr_result: Dict, correct_spelling: bool = True) -> Dict:
    """
    Process OCR result through NER pipeline.
    
    Args:
        ocr_result: Output from ocr.py
        correct_spelling: Whether to apply fuzzy correction
    
    Returns:
        Combined OCR + NER results
    """
    if not ocr_result.get("success", False):
        return {
            "success": False,
            "error": ocr_result.get("error", "OCR failed"),
            "drugs": [],
            "dosages": [],
            "routes": []
        }
    
    # Use corrected text from OCR
    text = ocr_result.get("corrected_text", ocr_result.get("raw_text", ""))
    
    # Extract drug info
    ner_result = extract_drug_info(text, correct_spelling)
    
    # Combine OCR dosages/routes with NER results
    combined_dosages = list(set(
        ocr_result.get("dosages", []) + ner_result.get("dosages", [])
    ))
    
    combined_routes = list(set(
        ocr_result.get("routes", []) + ner_result.get("routes", [])
    ))
    
    return {
        "success": True,
        "ocr_potential_drugs": ocr_result.get("potential_drug_names", []),
        "ner_drugs": ner_result.get("drugs", []),
        "corrected_drugs": ner_result.get("corrected_drugs", []),
        "dosages": combined_dosages,
        "routes": combined_routes,
        "raw_text": ocr_result.get("raw_text", ""),
        "corrected_text": ocr_result.get("corrected_text", ""),
        "all_entities": ner_result.get("all_entities", [])
    }

def train_custom_drug_ner(training_data: List[Dict], output_path: str = "models/custom_drug_ner"):
    """
    Train a custom NER model on drug-specific data.
    
    Args:
        training_data: List of dicts with 'text' and 'entities' keys
        output_path: Where to save the trained model
    
    Example training_data format:
    [
        {
            "text": "Take Advil 200mg orally twice daily",
            "entities": [
                {"start": 5, "end": 10, "label": "DRUG"},
                {"start": 11, "end": 16, "label": "DOSAGE"},
                {"start": 17, "end": 23, "label": "ROUTE"}
            ]
        }
    ]
    """
    nlp_model = load_nlp_model()
    
    # Convert training data to spaCy format
    train_examples = []
    for item in training_data:
        text = item["text"]
        entities = [(e["start"], e["end"], e["label"]) for e in item["entities"]]
        train_examples.append((text, {"entities": entities}))
    
    # Training logic would go here
    # This is a placeholder - actual training requires more setup
    print(f"Training on {len(train_examples)} examples...")
    print("Note: Full training implementation requires spaCy training loop")
    
    # Save model
    os.makedirs(output_path, exist_ok=True)
    nlp_model.to_disk(output_path)
    print(f"Model saved to {output_path}")

# Example usage
if __name__ == "__main__":
    # Test text extraction
    test_text = "Patient prescribed Lipitor 20mg orally once daily for cholesterol"
    result = extract_drug_info(test_text)
    
    print("Extracted Information:")
    print(f"Drugs: {result['drugs']}")
    print(f"Dosages: {result['dosages']}")
    print(f"Routes: {result['routes']}")
    
    if result['corrected_drugs']:
        print("\nCorrected Drug Names:")
        for correction in result['corrected_drugs']:
            print(f"  {correction['original']} -> {correction['corrected']} "
                  f"(confidence: {correction['confidence']}%)")