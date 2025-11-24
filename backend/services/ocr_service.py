"""
OCR Service - Extract text from medication images
"""
from typing import Dict, List
from backend.api.dependencies import get_claude_client
from backend.services.image_processor import ImageProcessor
from backend.utilities.prompt_builder import PromptBuilder


class OCRService:
    """Extract medication info from images using Claude Vision."""
    
    MODEL = "claude-sonnet-4-5-20250929"
    MAX_TOKENS = 1024
    
    def __init__(self):
        self.client = get_claude_client()
        self.image_processor = ImageProcessor()
    
    def process_images(self, images_bytes: List[bytes]) -> Dict:
        """Process images and extract medication info."""
        if not images_bytes:
            return self._error("No images provided")
        
        try:
            encoded = [self.image_processor.encode_to_base64(img) for img in images_bytes]
            text = self._call_claude(encoded)
            return self._success(text)
        except Exception as e:
            return self._error(str(e))
    
    def _call_claude(self, encoded_images: List[str]) -> str:
        """Call Claude API with encoded images."""
        content = self._build_content(encoded_images)
        
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            messages=[{"role": "user", "content": content}]
        )
        
        return response.content[0].text
    
    def _build_content(self, encoded_images: List[str]) -> List[Dict]:
        """Build message content with images and prompt."""
        content = []
        
        for img_b64 in encoded_images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_b64
                }
            })
        
        content.append({
            "type": "text",
            "text": PromptBuilder.ocr_extraction(len(encoded_images))
        })
        
        return content
    
    def _success(self, text: str) -> Dict:
        if not text or not text.strip():
            return self._error("No text detected")
        return {"success": True, "text": text.strip(), "error": None}
    
    def _error(self, message: str) -> Dict:
        return {"success": False, "text": "", "error": message}