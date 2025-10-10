import pytesseract
from PIL import Image
import re
from typing import Optional
import cv2
import numpy as np

# Common OCR error patterns for drug names
OCR_CORRECTIONS = {
    # Number/letter confusions
    "0": ["O", "o"],
    "1": ["l", "I", "|"],
    "5": ["S", "s"],
    "8": ["B"],
    
    # Common drug name fixes (build from your data)
    "Advi1": "Advil",
    "Tyl3nol": "Tylenol",
    "Aspirln": "Aspirin",
    "lbuprofen": "Ibuprofen",
    "Metf0rmin": "Metformin",
    "Lipit0r": "Lipitor",
    "Viagr4": "Viagra",
}

# Patterns to identify drug-related text
DOSAGE_PATTERN = r'\b\d+\.?\d*\s*(mg|mcg|ml|g|unit|units?|iu)\b'
ROUTE_KEYWORDS = [
    "oral", "orally", "by mouth", "po",
    "intravenous", "iv", "intravenously",
    "topical", "topically", "apply",
    "injection", "inject", "subcutaneous",
    "intramuscular", "im"
]

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess image for better OCR accuracy.
    """
    # Read image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Noise removal (optional)
    gray = cv2.medianBlur(gray, 3)
    
    return gray

def apply_ocr_corrections(text: str) -> str:
    """
    Apply known OCR error corrections.
    """
    corrected = text
    
    for wrong, right in OCR_CORRECTIONS.items():
        corrected = corrected.replace(wrong, right)
    
    return corrected

def extract_dosage_info(text: str) -> list[str]:
    """
    Extract dosage information from text.
    """
    dosages = re.findall(DOSAGE_PATTERN, text, re.IGNORECASE)
    return [d.strip() for d in dosages]

def extract_route_info(text: str) -> list[str]:
    """
    Extract route information from text.
    """
    text_lower = text.lower()
    routes = []
    
    for route in ROUTE_KEYWORDS:
        if route in text_lower:
            routes.append(route)
    
    return list(set(routes))  # Remove duplicates

def extract_potential_drug_names(text: str) -> list[str]:
    """
    Extract words that might be drug names (capitalized words, 3+ chars).
    This is a simple heuristic - MedSpacy will do better NER.
    """
    # Find capitalized words
    words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    
    # Filter out common words
    common_words = {"The", "And", "For", "Take", "With", "Before", "After", "Daily", "Twice"}
    potential_drugs = [w for w in words if w not in common_words]
    
    return potential_drugs

def extract_text_from_image(
    image_path: str,
    preprocess: bool = True,
    apply_corrections: bool = True
) -> dict:
    """
    Main OCR function with preprocessing and error correction.
    
    Args:
        image_path: Path to the image file
        preprocess: Whether to preprocess the image
        apply_corrections: Whether to apply OCR error corrections
    
    Returns:
        Dictionary with raw text, corrected text, and extracted info
    """
    try:
        if preprocess:
            # Preprocess image for better OCR
            processed_img = preprocess_image(image_path)
            # Convert numpy array back to PIL Image
            pil_img = Image.fromarray(processed_img)
        else:
            pil_img = Image.open(image_path)
        
        # Perform OCR
        raw_text = pytesseract.image_to_string(pil_img)
        
        # Apply corrections if enabled
        corrected_text = apply_ocr_corrections(raw_text) if apply_corrections else raw_text
        
        # Extract structured information
        dosages = extract_dosage_info(corrected_text)
        routes = extract_route_info(corrected_text)
        potential_drugs = extract_potential_drug_names(corrected_text)
        
        return {
            "raw_text": raw_text,
            "corrected_text": corrected_text,
            "dosages": dosages,
            "routes": routes,
            "potential_drug_names": potential_drugs,
            "success": True,
            "error": None
        }
    
    except Exception as e:
        return {
            "raw_text": "",
            "corrected_text": "",
            "dosages": [],
            "routes": [],
            "potential_drug_names": [],
            "success": False,
            "error": str(e)
        }

import io

def ocr_from_bytes(image_bytes: bytes, preprocess: bool = True) -> dict:
    """
    Perform OCR on image bytes (useful for FastAPI file uploads).
    """
    try:
        # Convert bytes to PIL Image
        img = Image.open(io.BytesIO(image_bytes))
        
        if preprocess:
            # Convert PIL to numpy for preprocessing
            img_array = np.array(img)
            # Preprocess
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            img = Image.fromarray(gray)
        
        # Perform OCR
        raw_text = pytesseract.image_to_string(img)
        corrected_text = apply_ocr_corrections(raw_text)
        
        return {
            "raw_text": raw_text,
            "corrected_text": corrected_text,
            "dosages": extract_dosage_info(corrected_text),
            "routes": extract_route_info(corrected_text),
            "potential_drug_names": extract_potential_drug_names(corrected_text),
            "success": True,
            "error": None
        }
    
    except Exception as e:
        return {
            "raw_text": "",
            "corrected_text": "",
            "dosages": [],
            "routes": [],
            "potential_drug_names": [],
            "success": False,
            "error": str(e)
        }

# Example usage
if __name__ == "__main__":
    result = extract_text_from_image("prescription.jpg")
    print("Raw Text:", result["raw_text"])
    print("\nCorrected Text:", result["corrected_text"])
    print("\nDosages:", result["dosages"])
    print("Routes:", result["routes"])
    print("Potential Drugs:", result["potential_drug_names"])