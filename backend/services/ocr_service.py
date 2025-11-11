"""
OCR Service using Claude API with Vision
"""
import io
import base64
from PIL import Image
from typing import Dict, List
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class OCRService:
    """
    OCR service using Claude's vision API for pill packaging text extraction.
    Supports single or multiple images in one API call.
    """
    
    def __init__(self, api_key: str):
        """Initialize Claude API client."""
        logger.info("Initializing Claude API client...")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        logger.info("Claude API ready")
    
    def process_images(self, images_bytes: List[bytes]) -> Dict:
        """
        Process multiple images witn CLAUDE API
        """
        try:
            if not images_bytes:
                return self._build_error_response("No images provided")
            
            # Optimize and encode all images
            encoded_images = []
            for img_bytes in images_bytes:
                optimized_img = self._load_and_optimize_image(img_bytes)
                img_b64 = self._encode_image_to_base64(optimized_img)
                encoded_images.append(img_b64)
            
            # Call Claude with all images at once
            extracted_text = self._call_claude_api_multi(encoded_images)
            return self._build_response(extracted_text)
            
        except Exception as e:
            logger.error(f"Claude OCR failed: {e}")
            return self._build_error_response(str(e))
    
    def _load_and_optimize_image(self, image_bytes: bytes) -> Image.Image:
        """Load image from bytes and optimize for API call."""
        img = Image.open(io.BytesIO(image_bytes))
        return self._optimize_image(img)
    
    def _encode_image_to_base64(self, img: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def _call_claude_api_multi(self, encoded_images: List[str]) -> str:
        """
        Make API call to Claude with multiple images
        to see all images together for better context.
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,  # Increased for multiple images
            messages=[
                {
                    "role": "user",
                    "content": self._build_multi_image_content(encoded_images),
                }
            ],
        )
        return message.content[0].text
    
    def _build_multi_image_content(self, encoded_images: List[str]) -> List[Dict]:
        """
        Build message content with multiple images.
        All images are sent before the text prompt.
        """
        content = []
        
        # Add all images first
        for img_b64 in encoded_images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_b64,
                },
            })
        
        # Add prompt after images
        content.append({
            "type": "text",
            "text": self._get_extraction_prompt_multi(len(encoded_images))
        })
        
        return content
    
    def _get_extraction_prompt_multi(self, num_images: int) -> str:
        """Get extraction prompt for multiple images."""
        if num_images == 1:
            return """Extract the following information from this medication packaging:
            - Brand name or product name
            - Drug/active ingredient name
            - Dosage form (tablet, capsule, caplet, liquid, cream, injection, etc.)
            - Route of administration (oral, topical, intravenous, etc.)

            Do NOT include warnings, age restrictions, directions, ingredients lists, or manufacturer details.
            Return only the relevant text, correcting any obvious OCR errors."""
        
        return f"""You are viewing {num_images} images of the same medication packaging from different angles.
        Extract the following information by looking across ALL images:
        - Brand name or product name
        - Drug/active ingredient name
        - Dosage form (tablet, capsule, caplet, liquid, cream, injection, etc.)
        - Route of administration (oral, topical, intravenous, etc.)

        IMPORTANT:
        - Combine information from all images to get the complete picture
        - If the brand name is on one image and the form is on another, include both
        - Cross-reference images to resolve any uncertainties
        - Only include information that is clearly visible

        Do NOT include warnings, age restrictions, directions, ingredients lists, or manufacturer details.
        Return only the relevant text, correcting any obvious OCR errors."""
    
    def _optimize_image(self, img: Image.Image, max_dimension: int = 1600) -> Image.Image:
        """Resize image if too large to save tokens."""
        width, height = img.size
        
        if width <= max_dimension and height <= max_dimension:
            return img
        
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _build_response(self, extracted_text: str) -> Dict:
        """Build successful response dictionary."""
        if not extracted_text or extracted_text.strip() == "":
            return self._build_error_response("No text detected")
        
        return {
            "success": True,
            "raw_text": extracted_text,
            "corrected_text": extracted_text,
            "error": None
        }
    
    def _build_error_response(self, error_message: str) -> Dict:
        """Build error response dictionary."""
        return {
            "success": False,
            "raw_text": "",
            "corrected_text": "",
            "error": error_message
        }