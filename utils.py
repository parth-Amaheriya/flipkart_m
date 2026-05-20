import json
import os
import gzip

PAGESAVE_DIR = "pagesaves3"

GEOCODE_DIR = os.path.join(PAGESAVE_DIR, "geocode_results")
RESPONSE1_DIR = os.path.join(PAGESAVE_DIR, "serviceability")
RESPONSE2_DIR = os.path.join(PAGESAVE_DIR, "product_details")
RESPONSE3_DIR = os.path.join(PAGESAVE_DIR, "parsed_products")

os.makedirs(GEOCODE_DIR, exist_ok=True)
os.makedirs(RESPONSE1_DIR, exist_ok=True)
os.makedirs(RESPONSE2_DIR, exist_ok=True)
os.makedirs(RESPONSE3_DIR, exist_ok=True)

os.makedirs(os.path.join(RESPONSE2_DIR, "html"), exist_ok=True)  # for raw HTML saves
os.makedirs(os.path.join(RESPONSE2_DIR, "json"), exist_ok=True)  # for JSON saves

def save_json(data, folder: str, filename: str):
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename + ".gz")

    with gzip.open(filepath, 'wt', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)