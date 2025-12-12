"""
API Routes - Drug lookup endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from ml.text_processor import TextProcessor
from services.drug_lookup_service import DrugLookupService
from services.dosage_service import DosageService
from services.ocr_service import OCRService

router = APIRouter()


# ==================== REQUEST MODELS ====================

class TextLookupRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    use_ner: bool = True


# ==================== SHARED LOGIC ====================

async def _process_lookup(
    processed: Dict,
    drug_lookup: DrugLookupService,
    dosage_service: DosageService
) -> Dict:
    """Shared drug lookup logic."""
    if "error" in processed:
        return {"success": False, "error": processed["error"]}
    
    # Lookup drug
    result = await drug_lookup.lookup_drug(
        brand_name=processed["brand_name"],
        dosage=processed.get("dosage"),
        route=processed.get("route"),
        form=processed.get("form")
    )
    
    
    # If exact match, get dosage info
    if result["status"] == "best_match":   
        dose_info = await dosage_service.get_dose(
            rxcui=result["product"]["rxcui"],
            weight_lb=processed.get("weight_lb"),
            age_months=processed.get("age_months"),
            dosage_numeric=processed.get("dosage_numeric")
        )
        
        return {
            "success": True,
            "status": "best_match",
            "brand_name": processed["brand_name"],
            "best_match": result["product"],      
            "dosage_info": dose_info           
        }
    
    # Multiple matches or not found
    return {
        "success": result["status"] != "not_found",
        "status": result["status"],
        "brand_name": processed["brand_name"],
        "matched_products": result["products"]
    }



# ==================== ENDPOINTS ====================

@router.post("/lookup/text")
async def lookup_from_text(request: TextLookupRequest):
    """Text-based drug lookup."""
    try:
        text_processor = TextProcessor()
        drug_lookup = DrugLookupService()
        dosage_service = DosageService()
        
        processed = text_processor.process_text(request.text, request.use_ner)
        return await _process_lookup(processed, drug_lookup, dosage_service)
    except Exception as e:
        # import traceback
        # traceback.print_exc()  # ADD THIS - prints full stack trace
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lookup/image")
async def lookup_from_image(
    files: List[UploadFile] = File(...),
    additional_text: Optional[str] = Form(None)
):
    """Image-based drug lookup with OCR."""
    
    # Validate
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images allowed")
    
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not an image"
            )
    
    try:
        ocr_service = OCRService()
        text_processor = TextProcessor()
        drug_lookup = DrugLookupService()
        dosage_service = DosageService()
        
        # Read and process images
        images_bytes = [await file.read() for file in files]
        ocr_result = ocr_service.process_images(images_bytes)
        
        if not ocr_result["success"]:
            return {
                "success": False,
                "error": ocr_result.get("error", "OCR failed")
            }
        
        # Combine OCR + user text
        combined_text = ocr_result["text"]
        if additional_text:
            combined_text += " " + additional_text
        
        # Process and lookup
        processed = text_processor.process_text(combined_text, use_ner=True)
        result = await _process_lookup(processed, drug_lookup, dosage_service)
        
        # Add metadata
        result["images_processed"] = len(files)
        if additional_text:
            result["user_provided_text"] = additional_text
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/clear-database")
async def clear_database():
    """Clear all cached drug data."""
    from api.dependencies import get_drug_database
    db = get_drug_database()
    db.clear()
    return {"success": True, "message": "Database cleared"}

@router.post("/health")
async def health_check():
    """Check database connection and cache status."""
    try:
        from api.dependencies import get_drug_database
        db = get_drug_database()
        stats = db.get_stats()
        db.close()
        
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "total_products": stats["total_products"],
                "total_brands": stats["total_brands"],
                "products_with_charts": stats["products_with_dosing_charts"],
                "size_mb": stats["db_size_mb"]
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": {
                "connected": False,
                "error": str(e)
            }
        }
