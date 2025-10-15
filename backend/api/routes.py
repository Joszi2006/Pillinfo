"""
API Routes - Orchestrates the correct flow
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from backend.services.text_processor import TextProcessor
from backend.services.drug_lookup_service import DrugLookupService
from backend.services.dosage_calculator import DosageCalculator
from backend.services.ocr_service import OCRService
from backend.services.cache_service import CacheService
import re

router = APIRouter()

# Dependency injection
def get_text_processor():
    processor = TextProcessor()
    # Inject cache into the processor's fuzzy matcher
    cache_service = CacheService()
    processor.inject_cache(cache_service.get_cache_dict())
    return processor

def get_drug_lookup_service():
    return DrugLookupService()

def get_dosage_calculator():
    return DosageCalculator()

def get_ocr_service():
    return OCRService()

def get_cache_service():
    return CacheService()

# ==================== REQUEST MODELS ====================

class TextLookupRequest(BaseModel):
    text: str = Field(..., description="User input text")
    patient_weight_kg: Optional[float] = None
    patient_age: Optional[int] = None
    use_ner: bool = True

class ManualLookupRequest(BaseModel):
    brand_name: str
    drug_dosage: Optional[str] = None
    route: Optional[str] = None
    form: Optional[str] = None

# ==================== ENDPOINTS ====================

@router.post("/lookup/text")
async def lookup_from_text(
    request: TextLookupRequest,
    text_processor: TextProcessor = Depends(get_text_processor),
    drug_lookup: DrugLookupService = Depends(get_drug_lookup_service),
    dosage_calc: DosageCalculator = Depends(get_dosage_calculator)
):
    """
    Stream 1: Text-based drug lookup
    
    Flow:
    1. User text → TextProcessor (NER + Fuzzy)
    2. Extracted drug → DrugLookupService (Cache/API)
    3. (Optional) Calculate dosage if weight provided
    """
    print(f"DEBUG ROUTE: Received request with text='{request.text}'")
    try:
        # Step 1: Process text (SHARED LOGIC)
      
        processed = text_processor.process_text(
            request.text, 
            request.use_ner,
            log_success=True  # 🎓 Enable Active Learning!
        )
        
        if not processed.get("brand_name"):
            return {
                "success": False,
                "error": "No drug name detected",
                "processed": processed
            }
        
        # Step 2: Look up drug products
        products, source = await drug_lookup.lookup_drug(processed["brand_name"])
        
        if not products:
            return {
                "success": False,
                "brand_name": processed["brand_name"],
                "products": [],
                "source": source,
                "processed": processed
            }
        
        # Step 3: Refine products based on extracted info
        refined = drug_lookup.refine_products(
            products,
            dosage=processed.get("dosage"),
            route=processed.get("route"),
            form=processed.get("form")
        )
        
        # Step 4: Extract numeric dosage for calculations
        dosage_mg = _extract_dosage_value(processed.get("dosage"))
        
        # Step 5: Calculate pediatric dosage if weight provided
        dosage_info = None
        if request.patient_weight_kg and dosage_mg:
            dosage_info = dosage_calc.calculate_pediatric_dosage(
                adult_dose_mg=dosage_mg,
                patient_weight_kg=request.patient_weight_kg,
                patient_age=request.patient_age
            )
        
        return {
            "success": True,
            "brand_name": processed["brand_name"],
            "best_match": refined[0] if refined else products[0],
            "matched_products": refined if refined else products[:5],
            "source": source,
            "processed": processed,
            "dosage_info": dosage_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lookup/image")
async def lookup_from_image(
    file: UploadFile = File(...),
    patient_weight_kg: Optional[float] = None,
    patient_age: Optional[int] = None,
    ocr_service: OCRService = Depends(get_ocr_service),
    text_processor: TextProcessor = Depends(get_text_processor),
    drug_lookup: DrugLookupService = Depends(get_drug_lookup_service),
    dosage_calc: DosageCalculator = Depends(get_dosage_calculator)
):
    """
    Stream 2: Image-based drug lookup
    
    Flow:
    1. Image → OCR Service (Image→Text)
    2. Extracted text → TextProcessor (NER + Fuzzy) ← SAME AS STREAM 1!
    3. Extracted drug → DrugLookupService (Cache/API) ← SAME AS STREAM 1!
    4. (Optional) Calculate dosage if weight provided
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Step 1: OCR - Convert image to text
        image_bytes = await file.read()
        ocr_result = ocr_service.process_image(image_bytes)
        
        if not ocr_result["success"]:
            return {
                "success": False,
                "error": "OCR failed",
                "ocr_result": ocr_result
            }
        
        # Step 2: Process text (SAME AS TEXT STREAM!)
        processed = text_processor.process_text(
            ocr_result["corrected_text"], 
            use_ner=True,
            log_success=True  # 🎓 Enable Active Learning!
        )
        
        if not processed.get("brand_name"):
            return {
                "success": False,
                "error": "No drug name detected in image",
                "ocr_result": ocr_result,
                "processed": processed
            }
        
        # Step 3: Look up drug (SAME AS TEXT STREAM!)
        products, source = await drug_lookup.lookup_drug(processed["brand_name"])
        
        if not products:
            return {
                "success": False,
                "brand_name": processed["brand_name"],
                "products": [],
                "source": source,
                "ocr_result": ocr_result,
                "processed": processed
            }
        
        # Step 4: Refine products
        refined = drug_lookup.refine_products(
            products,
            dosage=processed.get("dosage"),
            route=processed.get("route"),
            form=processed.get("form")
        )
        
        # Step 5: Calculate dosage if weight provided
        dosage_mg = _extract_dosage_value(processed.get("dosage"))
        dosage_info = None
        if patient_weight_kg and dosage_mg:
            dosage_info = dosage_calc.calculate_pediatric_dosage(
                adult_dose_mg=dosage_mg,
                patient_weight_kg=patient_weight_kg,
                patient_age=patient_age
            )
        
        return {
            "success": True,
            "brand_name": processed["brand_name"],
            "best_match": refined[0] if refined else products[0],
            "matched_products": refined if refined else products[:5],
            "source": source,
            "ocr_result": ocr_result,
            "processed": processed,
            "dosage_info": dosage_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lookup/manual")
async def lookup_manual(
    request: ManualLookupRequest,
    drug_lookup: DrugLookupService = Depends(get_drug_lookup_service)
):
    """
    Manual lookup - User provides structured fields
    Skips text processing, goes straight to drug lookup
    """
    try:
        products, source = await drug_lookup.lookup_drug(request.brand_name)
        
        if not products:
            return {
                "success": False,
                "brand_name": request.brand_name,
                "products": [],
                "source": source
            }
        
        refined = drug_lookup.refine_products(
            products,
            dosage=request.drug_dosage,
            route=request.route,
            form=request.form
        )
        
        return {
            "success": True,
            "brand_name": request.brand_name,
            "best_match": refined[0] if refined else products[0],
            "matched_products": refined if refined else products[:5],
            "source": source
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(
    cache_service: CacheService = Depends(get_cache_service)
):
    """Health check endpoint."""
    stats = cache_service.get_stats()
    return {
        "status": "healthy",
        "cache_stats": stats
    }


@router.post("/cache/seed")
async def seed_cache(
    cache_service: CacheService = Depends(get_cache_service)
):
    """Seed cache with common drugs."""
    result = await cache_service.seed_common_drugs()
    return result


# ==================== HELPER FUNCTIONS ====================

def _extract_dosage_value(dosage_str: str) -> Optional[float]:
    """Extract numeric value from dosage string."""
    if not dosage_str:
        return None
    match = re.search(r'(\d+\.?\d*)', dosage_str)
    if match:
        return float(match.group(1))
    return None