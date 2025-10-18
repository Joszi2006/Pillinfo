"""
API Routes - Orchestrates the correct flow (FIXED VERSION)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict
from functools import lru_cache
from backend.services.text_processor import TextProcessor
from backend.services.drug_lookup_service import DrugLookupService
from backend.services.dosage_calculator import DosageCalculator
from backend.services.ocr_service import OCRService
from backend.services.cache_service import CacheService
import asyncio

router = APIRouter()

# ==================== DEPENDENCY INJECTION (SINGLETON) ====================

@lru_cache()
def get_text_processor():
    """Singleton: Creates processor once and reuses it."""
    processor = TextProcessor()
    cache_service = get_cache_service()
    processor.inject_cache(cache_service.get_cache_dict())
    return processor

@lru_cache()
def get_drug_lookup_service():
    """Singleton: Reuses the same instance."""
    return DrugLookupService()

@lru_cache()
def get_dosage_calculator():
    """Singleton: Reuses the same instance."""
    return DosageCalculator()

@lru_cache()
def get_ocr_service():
    """Singleton: Reuses the same instance."""
    return OCRService()

@lru_cache()
def get_cache_service():
    """Singleton: Reuses the same instance."""
    return CacheService()

# ==================== REQUEST MODELS WITH VALIDATION ====================

class TextLookupRequest(BaseModel):
    text: str = Field(..., description="User input text", min_length=1, max_length=1000)
    patient_weight_kg: Optional[float] = Field(None, gt=0, lt=500, description="Weight in kg (1-500)")
    patient_age: Optional[int] = Field(None, gt=0, lt=120, description="Age in years (1-120)")
    use_ner: bool = True
    lookup_all_drugs : bool = False

class ManualLookupRequest(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    drug_dosage: Optional[str] = Field(None, max_length=50)
    route: Optional[str] = Field(None, max_length=50)
    form: Optional[str] = Field(None, max_length=50)

# ==================== SHARED LOGIC ====================

async def _process_drug_lookup(
    processed: Dict,
    patient_weight_kg: Optional[float],
    patient_age: Optional[int],
    drug_lookup: DrugLookupService,
    dosage_calc: DosageCalculator
) -> Dict:
    """
    Shared drug lookup logic for both text and image streams.
    
    This function consolidates Steps 3-6 that were duplicated in both endpoints.
    """
    if not processed.get("brand_name"):
        return {
            "success": False,
            "error": "No drug name detected",
            "processed": processed
        }
    
    # Use extracted weight/age OR fallback to request params
    patient_weight = processed.get("weight_kg") or patient_weight_kg
    patient_age = processed.get("age_years") or patient_age
    dosage_mg = processed.get("dosage_numeric")
    
    # Look up drug products
    products, source = await drug_lookup.lookup_drug(processed["brand_name"])
    
    if not products:
        return {
            "success": False,
            "brand_name": processed["brand_name"],
            "products": [],
            "source": source,
            "processed": processed
        }
    
    # Refine products based on extracted info
    refined = drug_lookup.refine_products(
        products,
        dosage=processed.get("dosage"),
        route=processed.get("route"),
        form=processed.get("form")
    )
    
    # Calculate pediatric dosage if weight provided
    dosage_info = None
    if patient_weight and dosage_mg:
        dosage_info = dosage_calc.calculate_pediatric_dosage(
            adult_dose_mg=dosage_mg,
            patient_weight_kg=patient_weight,
            patient_age=patient_age
        )
    
    return {
        "success": True,
        "brand_name": processed["brand_name"],
        "best_match": refined[0] if refined else products[0],
        "matched_products": refined if refined else products[:5],
        "source": source,
        "processed": processed,
        "dosage_info": dosage_info,
        "extracted_weight": processed.get("weight_kg"),
        "extracted_age": processed.get("age_years")
    }

# ==================== ENDPOINTS ====================

@router.post("/lookup/text")
async def lookup_from_text(
    request: TextLookupRequest,
    text_processor: TextProcessor = Depends(get_text_processor),
    drug_lookup: DrugLookupService = Depends(get_drug_lookup_service),
    dosage_calc: DosageCalculator = Depends(get_dosage_calculator)
):
    """
    Text-based drug lookup
    
    Flow:
    1. User text → TextProcessor (NER + Fuzzy)
    2. Extracted drug → DrugLookupService (Cache/API)
    3. (Optional) Calculate dosage if weight provided
    """
    try:
        # Step 1: Process text (extracts everything)
        processed = text_processor.process_text(request.text, request.use_ner)
        all_drugs = processed.get("all_drugs", [])
        
        # Step 2: Check if multiple drugs detected
        if len(all_drugs) > 1 and request.lookup_all_drugs:
            # User wants ALL drugs - lookup in parallel
            tasks = [drug_lookup.lookup_drug(drug) for drug in all_drugs]
            results = await asyncio.gather(*tasks)
            
            return {
                "success": True,
                "multiple_drugs": True,
                "count": len(all_drugs),
                "results": [
                    {
                        "drug": all_drugs[i],
                        "products": results[i][0],
                        "source": results[i][1]
                    }
                    for i in range(len(all_drugs))
                ]
            }
        
        # Step 3: Default behavior - lookup first drug only
        result = await _process_drug_lookup(
            processed,
            request.patient_weight_kg,
            request.patient_age,
            drug_lookup,
            dosage_calc
        )
        
        # Step 4: Add warning if multiple drugs detected
        if len(all_drugs) > 1:
            result["multiple_drugs_warning"] = {
                "message": f"Multiple drugs detected. Showing results for: {processed['brand_name']}",
                "all_detected": all_drugs,
                "other_drugs": all_drugs[1:]
            }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lookup/image")
async def lookup_from_image(
    file: UploadFile = File(...),
    patient_weight_kg: Optional[float] = Form(None),
    patient_age: Optional[int] = Form(None),
    ocr_service: OCRService = Depends(get_ocr_service),
    text_processor: TextProcessor = Depends(get_text_processor),
    drug_lookup: DrugLookupService = Depends(get_drug_lookup_service),
    dosage_calc: DosageCalculator = Depends(get_dosage_calculator)
):
    """
    Stream 2: Image-based drug lookup
    
    Flow:
    1. Image → OCR Service (Image→Text)
    2. Extracted text → TextProcessor (NER + Fuzzy)
    3. Extracted drug → DrugLookupService (Cache/API)
    4. (Optional) Calculate dosage if weight provided
    """
    # Validate form data manually since Form() doesn't support validators
    if patient_weight_kg is not None and (patient_weight_kg <= 0 or patient_weight_kg >= 500):
        raise HTTPException(status_code=400, detail="patient_weight_kg must be between 0 and 500")
    
    if patient_age is not None and (patient_age <= 0 or patient_age >= 120):
        raise HTTPException(status_code=400, detail="patient_age must be between 0 and 120")
    
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
            use_ner=True
        )
        
        # Step 3-6: Shared logic
        result = await _process_drug_lookup(
            processed,
            patient_weight_kg,
            patient_age,
            drug_lookup,
            dosage_calc
        )
        
        # Add OCR result to response
        result["ocr_result"] = ocr_result
        
        return result
    
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