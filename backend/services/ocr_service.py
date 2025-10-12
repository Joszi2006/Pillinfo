"""
OCR Service - Image processing only
Single Responsibility: Convert images to text
"""
import io
from PIL import Image
import pytesseract
import cv2
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """
    Handles OCR processing with preprocessing and error correction.
    Wraps ocr.py functionality into a service.
    """
    
    # Common OCR error patterns
    OCR_CORRECTIONS = {
        "Lipit0r": "Lipitor",
        "Tyl3nol": "Tylenol",
        "Aspirln": "Aspirin",
        "lbuprofen": "Ibuprofen",
        "Metf0rmin": "Metformin",
        "Viagr4": "Viagra",
        "Advi1": "Advil",
        "0rally": "orally",
        "2Omg": "20mg",
    }
    
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6'
    
    def process_image(self, image_bytes: bytes, preprocess: bool = True) -> Dict:
        """
        Main OCR processing method.
        
        Args:
            image_bytes: Image file as bytes
            preprocess: Whether to apply preprocessing
        
        Returns:
            Dictionary with OCR results and metadata
        """
        try:
            # Convert bytes to PIL Image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess if enabled
            if preprocess:
                img = self._preprocess_image(img)
            
            # Perform OCR
            raw_text = pytesseract.image_to_string(img, config=self.tesseract_config)
            
            # Apply corrections
            corrected_text = self._apply_corrections(raw_text)
            
            return {
                "success": True,
                "raw_text": raw_text,
                "corrected_text": corrected_text,
                "preprocessing_applied": preprocess,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return {
                "success": False,
                "raw_text": "",
                "corrected_text": "",
                "preprocessing_applied": False,
                "error": str(e)
            }
    
    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        
        Steps:
        1. Convert to grayscale
        2. Apply thresholding
        3. Denoise
        """
        # Convert PIL to numpy array
        img_array = np.array(img)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply adaptive thresholding
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Denoise
        gray = cv2.medianBlur(gray, 3)
        
        # Convert back to PIL Image
        return Image.fromarray(gray)
    
    def _apply_corrections(self, text: str) -> str:
        """
        Apply known OCR error corrections.
        
        Args:
            text: Raw OCR text
        
        Returns:
            Corrected text
        """
        corrected = text
        
        for wrong, right in self.OCR_CORRECTIONS.items():
            corrected = corrected.replace(wrong, right)
        
        return corrected
    
    def add_correction(self, wrong: str, right: str):
        """
        Add a new OCR correction pattern.
        Useful for learning from mismatches.
        
        Args:
            wrong: Incorrect OCR output
            right: Correct text
        """
        self.OCR_CORRECTIONS[wrong] = right
        logger.info(f"Added OCR correction: {wrong} -> {right}")
    
    def get_corrections(self) -> Dict[str, str]:
        """Get all registered corrections."""
        return self.OCR_CORRECTIONS.copy()