from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rapidfuzz import process, fuzz
from backend.util import load_cached_labels, save_cached_labels
import requests

app = FastAPI(title="Drug Info Chatbot Backend")

# ---- Pydantic Models ----
class ProductRequest(BaseModel):
    brand_name: str
    drug_dosage: str | None = None
    route: str | None = None

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

def get_or_fetch_products(brand_name: str):
    """Check cache for brand products, else fetch from API and update cache."""
    cached_labels = load_cached_labels()

    # Normalize brand name
    brand = brand_name.strip().title()

    # Step 1: Return cached if available
    if brand in cached_labels:
        return cached_labels[brand], "cache"

    # Step 2: Fetch from API if not cached
    products = fetch_from_api(brand)
    if not products:
        return [], "api"  # still return consistent structure

    # Step 3: Cache the new result
    cached_labels[brand] = products
    save_cached_labels(cached_labels)

    return products, "api"

@app.post("/get_products")
def get_products(request: ProductRequest):
    brand = request.brand_name.strip().title()
    dosage = request.drug_dosage.strip() if request.drug_dosage else None
    route = request.route.strip() if request.route else None

    # 🔹 Use helper
    products, source = get_or_fetch_products(brand)

    if not products:
        return {"brand": brand, "products": [], "source": source, "note": "No products found"}

    # If dosage or route provided, refine results
    if dosage or route:
        user_query = " ".join(filter(None, [brand, dosage, route])).lower()

        # Try exact substring matches
        matches = [p for p in products if user_query in p.lower()]

        # Fuzzy fallback
        if not matches:
            best = process.extractOne(user_query, products, scorer=fuzz.WRatio)
            if best and best[1] > 70:
                matches = [best[0]]

        return {
            "brand": brand,
            "full_product": matches[0] if matches else None,
            "products_checked": len(products),
            "source": source,
            "note": "Match found" if matches else "No exact or close match found"
        }

    # If only brand provided, return all products
    return {
        "brand": brand,
        "products": products,
        "source": source,
        "note": "Returning all products for this brand"
    }
