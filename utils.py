import json
import os
import gzip
from datetime import datetime
date= datetime.now().strftime("%Y_%m_%d")

PAGESAVE_DIR = "pagesaves_" + date
os.makedirs(PAGESAVE_DIR, exist_ok=True)

SUGGESTION_DIR = os.path.join(PAGESAVE_DIR, "suggestion_results")
LAT_LNG_DIR = os.path.join(PAGESAVE_DIR, "lat_lng_results")
GEOCODE_DIR_2 = os.path.join(PAGESAVE_DIR, "geocode_results_2")
UPDATE_DIR = os.path.join(PAGESAVE_DIR, "update")
RESPONSE1_DIR = os.path.join(PAGESAVE_DIR, "serviceability")
RESPONSE2_DIR = os.path.join(PAGESAVE_DIR, "product_details")
# RESPONSE3_DIR = os.path.join(PAGESAVE_DIR, "parsed_products")


os.makedirs(SUGGESTION_DIR, exist_ok=True)
os.makedirs(LAT_LNG_DIR, exist_ok=True)
os.makedirs(GEOCODE_DIR_2, exist_ok=True)
os.makedirs(UPDATE_DIR, exist_ok=True)
os.makedirs(RESPONSE1_DIR, exist_ok=True)
os.makedirs(RESPONSE2_DIR, exist_ok=True)

def save_json(data, folder: str, filename: str):
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename + ".gz")

    with gzip.open(filepath, 'wt', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)