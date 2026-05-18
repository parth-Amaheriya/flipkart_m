import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

from curl_cffi import requests

import db as db_handler
from parser import parse_json_file

# ======================= CONFIG =======================
MAX_WORKERS = 8

# Page Save Folders
PAGESAVE_DIR = "pagesaves"
GEOCODE_DIR = os.path.join(PAGESAVE_DIR, "geocode_results")
RESPONSE1_DIR = os.path.join(PAGESAVE_DIR, "serviceability")
RESPONSE2_DIR = os.path.join(PAGESAVE_DIR, "product_details")
RESPONSE3_DIR = os.path.join(PAGESAVE_DIR, "parsed_products")

os.makedirs(GEOCODE_DIR, exist_ok=True)
os.makedirs(RESPONSE1_DIR, exist_ok=True)
os.makedirs(RESPONSE2_DIR, exist_ok=True)
os.makedirs(RESPONSE3_DIR, exist_ok=True)

# ======================= HEADERS (same as before) =======================
HEADERS = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': 'T=TI177882628280400144292814443773535942707683402644789381544400348835; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFkOTYzYzUwLTM0YjctNDA1OC1iMTNmLWY2NDhiODFjYTBkYSJ9.eyJleHAiOjE3ODA1NTQyODIsImlhdCI6MTc3ODgyNjI4MiwiaXNzIjoia2V2bGFyIiwianRpIjoiNzczYzA5N2YtMjQ1Ny00OWE5LWI5YjktNDkwNTVmNzhkNTJiIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzc4ODI2MjgyODA0MDAxNDQyOTI4MTQ0NDM3NzM1MzU5NDI3MDc2ODM0MDI2NDQ3ODkzODE1NDQ0MDAzNDg4MzUiLCJrZXZJZCI6IlZJQjJFMjM2RjQwODJENDc4RThBQzY1Q0IxREY0MTRBNjUiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJDSCIsIm0iOnRydWUsImdlbiI6M30.g-i9IpnBfwTAK8bIHAV1VawxLH4TMoJC4eSAMc_qhls; K-ACTION=null; Network-Type=4g; vw=1707; dpr=1.125; vh=379; vd=VIB2E236F4082D478E8AC65CB1DF414A65-1778826284228-1.1778828065.1778826284.154617709; ud=1.3RovXtHZlV6Ku4MnxYAGp39Vlbw8kwPMets-6UKtBT3-o9uQqHjgWMuzD7MTvhcEij-Oyd3iW-boJ1at_lQyVXwrBWhNxWqD-j-Gly0ojdcykq7H_YQtABjYU6S0pMOGI2XOKOLiBDcub0mdnsGllFc1vkZRRBXTVGrswaX9gpPRj3ITjBzSyc4xLaKxXoJZsWlMlrcBMJpz7vpgYZeveaLl2VjCatEgpGSOz1C8vDR7O4o9d3BTCX_Bu0eGnXYYcDPdz-M39LrqwA1YfP3X09eZM1uqmn24ncFEHqxiduzv84rKk7snwI62IWYW9jW0L5V7bnlaC01Tc2w4yioAjfhTkWsiX-Z5tyfTx3UXx2hfQqZh7gW_RFEJlHzARb3D7iENlehIph_gqUGb-eNPxcx_DfjAZotKb6fq1RmfueS0n4ksuDC2CmXqc5SZUJgAXSSm9lfkqV1upaSQ6CbtViowJae9lyCNKOHflQdh0-0VVjYVmFC6qZio9KNAD6kY6YHNG4sUMIDCyL-97eK9Ig; S=d1t18fj8/Nh1jSQ8vP0AnPz9MP6rhBkjYIMqOp7qWalV7TowAEp8uChwx/LbJ5XdZRwikh/BuZ5awsZ4/W+m9GswFlA==; SN=VIB2E236F4082D478E8AC65CB1DF414A65.TOK3B537A9167DB44C4AA51E33F49C0D84B.1778828074893.LO',
        'Origin': 'https://www.flipkart.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.flipkart.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
        'X-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36 FKUA/website/41/website/Desktop',
        'flipkart_secure': 'true',
        'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

# ======================= HELPER FUNCTIONS =======================
def save_json(data, folder: str, filename: str):
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_lat_long_from_pincode(pincode: str):
    api_key = "AIzaSyAtKsoYaqKOXMV00f9qLDAgbYYevlxAGsQ"
    params = {"address": f"{pincode}, IN", "key": api_key, "components": f"postal_code:{pincode}"}

    try:
        resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params)
        data = resp.json()
        save_json(data, GEOCODE_DIR, f"geocode_{pincode}.json")

        if data.get("status") != "OK" or not data.get("results"):
            return None

        result = data["results"][0]
        loc = result["geometry"]["location"]
        locality=result.get("formatted_address")
        return {
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "city": next((comp["long_name"] for comp in result.get("address_components", [])
                         if "locality" in comp.get("types", [])), None),
            "locality": locality
        }
    except Exception as e:
        print(f"Geocode Error for {pincode}: {e}")
        return None


def check_serviceability(latitude, longitude, pincode: str) -> bool:
    try:
        url = 'https://1.rome.api.flipkart.com/api/1/location/serviceability'
        payload = {'latitude': latitude, 'longitude': longitude}

        resp = requests.post(url, headers=HEADERS, json=payload, impersonate='chrome')
        save_json(resp.json(), RESPONSE1_DIR, f"serviceability_{pincode}.json")

        return resp.json().get('RESPONSE', {}).get('serviceable', False)
    except Exception as e:
        print(f"Serviceability Error for {pincode}: {e}")
        return False


def fetch_product_details(pageuri: str, pincode: str):
    try:
        url = 'https://1.rome.api.flipkart.com/api/4/page/fetch'
        payload = {
            'pageUri': pageuri,
            'pageContext': {
                'trackingContext': {'context': {'eVar51': 'direct_browse', 'eVar61': 'direct_browse'}},
                'networkSpeed': 9350
            },
            'locationContext': {'pincode': pincode, 'changed': False},
        }

        resp = requests.post(url, params={'cacheFirst': 'false'}, headers=HEADERS, json=payload, impersonate='chrome')
        data = resp.json()
        schema = data.get('RESPONSE', {}).get('pageData', {}).get('seoData', {}).get('schema', [{}])[0]

        save_json(data, RESPONSE2_DIR, f"product_{pincode}_{schema.get('sku')}.json")
        
        parse_data=parse_json_file(data)

        with open(os.path.join(RESPONSE3_DIR, f"parsed_product_{pincode}_{schema.get('sku')}.json"), 'w', encoding='utf-8') as f:
            json.dump(parse_data, f, indent=2, ensure_ascii=False)

        context=data.get('RESPONSE', {}).get('pageData', {}).get('pageContext', {})
        if context.get('fdpEventTracking', {}).get('events', {}).get('psi', {}).get('pls', {}).get('availabilityStatus') == 'IN_STOCK':
            stock_status = "YES"
        else:            
            stock_status = "NO"    
        return {
            "sku": schema.get('sku'),
            "product_name": schema.get('name'),
            "brand": schema.get('brand', {}).get('name'),
            "stock_avaliblity_status": stock_status,
            "product_data": parse_data
        }
    except Exception as e:
        print(f"Product Fetch Error: {e}")
        return {}



# ======================= NEW: DELIVERABLE PINCODE CHECK =======================
def process_pincode_for_deliverability(record: Dict):
    record_id = record['id']
    pincode = record['pincode']
    location = record.get('location')

    print(f"Checking deliverability for pincode: {pincode}")

    geo = get_lat_long_from_pincode(pincode)
    if not geo:
        print(f"Geocoding failed for {pincode}")
        db_handler.update_status(record_id, "failed")
        return

    is_serviceable = check_serviceability(geo['latitude'], geo['longitude'], pincode)

    if is_serviceable:
        print(f"✅ Deliverable: {pincode} | City: {geo.get('city')}")
        db_handler.insert_deliverable_pincode(
            pincode, 
            geo['latitude'], 
            geo['longitude'], 
            geo.get('city'),
            geo.get('locality'),
            location
        )
        db_handler.update_status(record_id, "done")
    else:
        print(f"❌ Not Deliverable: {pincode}")
        db_handler.update_status(record_id, "not_serviceable")


# ======================= MAIN WORKER (Product Scraping) =======================
def process_record(record: Dict):
    record_id = record['id']
    url = record['url']
    pincode = record['pincode']

    if "http" in url:
        url = url.split("flipkart.com")[-1]

    try:
        print(f"Processing → {url} | Pin: {pincode}")

        # Fetch from deliverable table instead of re-checking
        prod_data = fetch_product_details(url, pincode)

        result = {
            "sku": prod_data.get('sku'),
            "url": url,
            "pincode": pincode,
            "city": record.get('city'),          # from deliverable table
            "product_name": prod_data.get('product_name'),
            "brand": prod_data.get('brand'),
            "stock_avaliblity_status": prod_data.get('stock_avaliblity_status'),
            "EAN_code": None,
            "product_data": prod_data.get('product_data')
        }

        db_handler.insert_product_data(result)
        db_handler.update_status(record_id, "done")
        print(f"Saved to DB: {url} | Pin: {pincode}")

    except Exception as e:
        print(f"Error processing {url}: {e}")
        db_handler.update_status(record_id, "failed")


# ======================= MAIN =======================
def main():
    db_handler.create_tables()

    print("=== Step 1: Checking Pincode Deliverability ===\n")
    while True:
        unique_pincode_rows = db_handler.get_unique_pending_pincodes()

        if not unique_pincode_rows:
            print("No new pincodes to check.")
            break

        print(f"Found {len(unique_pincode_rows)} unique pincodes to check.\n")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_pincode_for_deliverability, record) for record in unique_pincode_rows]
            for future in as_completed(futures):
                future.result()

    print("\n=== Step 2: Starting Product Scraping (Only Deliverable Pincodes) ===\n")

    while True:
        pending = db_handler.get_deliverable_pincodes()   # You may want to modify this too
        if not pending:
            print("No more pending records. Finished!")
            break

        print(f"Processing {len(pending)} records with {MAX_WORKERS} threads...\n")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_record, rec) for rec in pending]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Thread Error: {e}")

        time.sleep(2)


if __name__ == "__main__":
    main()