from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI(title="Drug Info Chatbot Backend")

# Path to your existing cached labels file
CACHED_FILE = "data/cached_labels.json"

# Ensure the file exists
if not os.path.exists(CACHED_FILE):
    with open(CACHED_FILE, "w") as f:
        json.dump({}, f)

class BrandRequest(BaseModel):
    brand_name: str

def load_cached_labels():
    with open(CACHED_FILE, "r") as f:
        return json.load(f)

def save_cached_labels(labels_dict):
    with open(CACHED_FILE, "w") as f:
        json.dump(labels_dict, f, indent=2)

def fetch_from_api(brand_name: str):
    """Query RxNorm API for a brand and return product variants."""
    url = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={brand_name}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    data = resp.json()

    concept_groups = data.get("drugGroup", {}).get("conceptGroup", [])
    products = []
    for group in concept_groups:
        if group.get("tty") in ["SBD", "BN", "SCD"]:
            for cp in group.get("conceptProperties", []):
                name = cp.get("synonym", "")
                if name and name not in products:
                    products.append(name)        
    return products

@app.post("/get_products")
def get_brand_products(request: BrandRequest):
    brand_name = request.brand_name.strip().title()  # normalize capitalization
    cached_labels = load_cached_labels()

    # Check cache first
    if brand_name in cached_labels:
        return {"brand": brand_name, "products": cached_labels[brand_name], "source": "cache"}

    # Not in cache, fetch from API
    products = fetch_from_api(brand_name)
    if not products:
        return {"brand": brand_name, "products": [], "source": "api", "note": "No products found"}

    # Save to cache
    cached_labels[brand_name] = products
    save_cached_labels(cached_labels)

    return {"brand": brand_name, "products": products, "source": "api"}
fetch_from_api("advil")