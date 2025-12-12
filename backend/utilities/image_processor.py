"""
Image Processor - Handle image optimization and encoding
"""
import io
import base64
from PIL import Image


class ImageProcessor:
    """Process images for API consumption."""
    
    MAX_DIMENSION = 1600
    
    def encode_to_base64(self, image_bytes: bytes) -> str:
        """Load, resize, and encode image to base64."""
        img = self._load(image_bytes)
        img = self._resize(img)
        return self._to_base64(img)
    
    def _load(self, image_bytes: bytes) -> Image.Image:
        """Load image from bytes."""
        return Image.open(io.BytesIO(image_bytes))
    
    def _resize(self, img: Image.Image) -> Image.Image:
        """Resize if exceeds max dimension."""
        width, height = img.size
        
        if width <= self.MAX_DIMENSION and height <= self.MAX_DIMENSION:
            return img
        
        if width > height:
            new_width = self.MAX_DIMENSION
            new_height = int(height * (self.MAX_DIMENSION / width))
        else:
            new_height = self.MAX_DIMENSION
            new_width = int(width * (self.MAX_DIMENSION / height))
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _to_base64(self, img: Image.Image) -> str:
        """Encode image to base64 string."""
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")