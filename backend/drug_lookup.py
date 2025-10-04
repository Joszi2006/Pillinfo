from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from difflib import get_close_matches
from util import load_cached_labels, save_cached_labels
import requests

app = FastAPI(title="Drug Info Chatbot Backend")

# ---- Pydantic Models ----
class BrandRequest(BaseModel):
    brand_name: str

class FullProductRequest(BaseModel):
    brand_name: str
    drug_dosage: str
    route: str


# ---- RxNorm API Helper ----
def fetch_from_api(brand_name: str):
    """Query RxNorm API for a brand and return product variants."""
    url = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={brand_name}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    data = resp.json()
    concept_groups = data.get("drugGroup", {}).get("conceptGroup", [])
    products = []

    for group in concept_groups:
        if group.get("tty") in ["SBD", "BN", "SCD"]:
            for cp in group.get("conceptProperties", []):
                name = cp.get("synonym") or cp.get("name")
                if name and name not in products:
                    products.append(name)
    return products


# ---- Brand Lookup ----
@app.post("/get_products")
def get_brand_products(request: BrandRequest):
    brand_name = request.brand_name.strip().title()
    cached_labels = load_cached_labels()

    # Step 1: Check cache
    if brand_name in cached_labels:
        return {"brand": brand_name, "products": cached_labels[brand_name], "source": "cache"}

    # Step 2: Fetch from API
    products = fetch_from_api(brand_name)
    if not products:
        return {"brand": brand_name, "products": [], "source": "api", "note": "No products found"}

    # Step 3: Cache and return
    cached_labels[brand_name] = products
    save_cached_labels(cached_labels)

    return {"brand": brand_name, "products": products, "source": "api"}


# ---- Full Product Validation ----
@app.post("/get_full_products")
def get_full_products(request: FullProductRequest):
    brand = request.brand_name.strip().title()
    dosage = request.drug_dosage.strip()
    route = request.route.strip()

    # Reuse get_brand_products logic (without double caching)
    result = get_brand_products(BrandRequest(brand_name=brand))
    products = result["products"]

    if not products:
        return {
            "brand": brand,
            "full_product": None,
            "note": "No products found for this brand"
        }

    # Combine user’s full input (normalize)
    user_input_full = f"{brand} {dosage} {route}".lower()

    # Try exact substring match first
    matches = [p for p in products if user_input_full in p.lower()]

    # If no direct match, try fuzzy matching
    matched = matches[0] if matches else (
        get_close_matches(user_input_full, products, n=1, cutoff=0.6)[0]
        if get_close_matches(user_input_full, products, n=1, cutoff=0.6)
        else None
    )

    return {
        "brand": brand,
        "full_product": matched,
        "products_checked": len(products),
        "source": result["source"],
        "note": "Match found" if matched else "No exact or close match found"
    }
