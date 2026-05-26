import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
from urllib.parse import urlparse, parse_qs
from curl_cffi import requests

from utils import (
    GEOCODE_DIR,
    UPDATE_DIR,
    RESPONSE1_DIR,
    RESPONSE2_DIR,
    save_json
)

import db as db_handler
from parser import parse_json_file

# from call_html import fetch_product_details

# ======================= CONFIG =======================
MAX_WORKERS = 10

# ======================= HEADERS (same as before) =======================
HEADERS =  {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://www.flipkart.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.flipkart.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'X-User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 FKUA/msite/0.0.4/msite/Mobile',
    'flipkart_secure': 'true',
    'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'T=TI177933813735000087741217135396657343599418698600319723431969621358; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFkOTYzYzUwLTM0YjctNDA1OC1iMTNmLWY2NDhiODFjYTBkYSJ9.eyJleHAiOjE3ODEwNjYxMzcsImlhdCI6MTc3OTMzODEzNywiaXNzIjoia2V2bGFyIiwianRpIjoiMTliOTIxNTEtNGVmOS00YzI2LWI2MTEtMGUxZTU4Mzg0YzVkIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzc5MzM4MTM3MzUwMDAwODc3NDEyMTcxMzUzOTY2NTczNDM1OTk0MTg2OTg2MDAzMTk3MjM0MzE5Njk2MjEzNTgiLCJrZXZJZCI6IlZJNjE4Rjk3OEJGMDQ2NDcyMkE3NUMzOEZBNzY1MkUzODIiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjN9.eMvBYdg5AcTMfFd4_t3UZkChgUcj-M6947MNhkiju6o; K-ACTION=null; vh=322; vw=1707; dpr=1.125; vd=VI618F978BF0464722A75C38FA7652E382-1779338138574-1.1779338138.1779338138.152368956; ud=8.H-ln8QiRdJI2Sd_6H6Ww6mCGs5k2lJvvabgQRdssG52XxQ245xgf3YrVa8ovhe7d4bDKJRuoob1zkpcAgyVelYixRfQpLgtdOzKp40ByzWT9ui1-6P9vX45J1J-o782Yf_IMFz8woDy2CmkeGaVkB2LLywXsLD7dcQ8LWnvn_mGHpC7iN4wVYLpgtnuRgbhCm5it_yRHpeCXcPhfBYYhB74967tN7qutMkqtC12hxxSv6gvWO1Q--3hLeTdzeGNeT2BTxyyFUbVEfFiEUgLIMiAjU0Of8gIDMItk3zddcVW5KRb-prbVIVJqDH53hnNuz-cI4_4CD_8VAWdRUFN1g8ksG-qN5Z74n016OfSYcZ3-6m35IRnJOduMdRY2OKw0ejF6Ju512K9it-YeSl7HCPJhEp-tSEd3PNTWsAhrXmjS0eKPcl5Z0ptdcD5qwfT23nkAwDgxm7QSRTe128ZXfAFacNu8bXV1LGdNGsh_i_BHFMn5jeNPZBXCdftfYWQ3M_rBFgh6hfrv8NinW0Aj_Q; S=d1t19WEE/IAM/Ij8/GCZYRj9WP+IgEcv2WQhsaf6re4n8ontP9lE4YOiQkw7kPHa7QxaB1bnONgf/PB6AG6jVf8TWTA==; SN=VI618F978BF0464722A75C38FA7652E382.TOK72F03336D0C64DE6A36E2967EC8BB110.1779338160229.LO',
}

# ======================= HELPER FUNCTIONS =======================
import gzip


def extract_location_data(data):
    if not data or data.get("status") != "OK" or not data.get("results"):
        return None, "No results or API error"

    result = data["results"][0]   # Best match

    loc = result["geometry"]["location"]
    address_components = result["address_components"]

    latitude = loc["lat"]
    longitude = loc["lng"]

    city = None
    locality = result.get("formatted_address")
    state = None
    pincode_extracted = None

    for component in address_components:
        types = component["types"]
        
        if "locality" in types and not city:                    # City / Town
            city = component["long_name"]
        
        elif "administrative_area_level_1" in types:            # State
            state = component["long_name"]
        
        elif "postal_code" in types:                            # Pincode
            pincode_extracted = component["long_name"]

    # Fallbacks
    if not city:
        # Try administrative_area_level_2 or sublocality as city
        for component in address_components:
            if "administrative_area_level_2" in component["types"]:
                city = component["long_name"]
                break
    print("locality",locality)
    return {
        "latitude": latitude,
        "longitude": longitude,
        "city": city,
        "locality": locality,
        "state": state,
        "pincode": pincode_extracted
    }, None

def get_lat_long_from_pincode(pincode: str):
    api_key = "AIzaSyAtKsoYaqKOXMV00f9qLDAgbYYevlxAGsQ"
    params = {"address": f"{pincode}, IN", "key": api_key, "components": f"postal_code:{pincode}"}
    data = None
    error_message = None

    try:
        resp = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params)
        print(resp)
        data = resp.json()

        if data.get("status") != "OK" or not data.get("results"):
            return None
        extracted_data, error = extract_location_data(data)
        if error:
            return {"error": error}
        
        # result = data["results"][0]
        # loc = result["geometry"]["location"]
        # locality=result.get("formatted_address")
        # city=state=None
        # for component in result.get("address_components", []):
        #     if 'locality' in component['types']:
        #         city=component['long_name']

        #     if 'administrative_area_level_1' in component['types']:
        #         state=component['long_name']
        # if city is None and state is not None:
        #     print(city,state)
        #     return {'error':"City or state not found in geocode result"}
        # loc_info={
        #     "latitude": loc["lat"],
        #     "longitude": loc["lng"],
        #     "city": city,
        #     "locality": locality,
        #     "state": state,
        #     "pincode": pincode
        # }
        return extracted_data
    
    except Exception as e:
        error_message = str(e)
        print(f"Geocode Error for {pincode}: {e}")
        return None
    finally:
        save_json(
            data if data is not None else {"pincode": pincode, "error": error_message, "source": "geocode"},
            GEOCODE_DIR,
            f"geocode_{pincode}.json"
        )


def check_serviceability(latitude, longitude, pincode: str) -> bool:
    data = None
    error_message = None

    try:
        url = 'https://1.rome.api.flipkart.com/api/1/location/serviceability'
        payload = {'latitude': latitude, 'longitude': longitude}

        resp = requests.post(url, headers=HEADERS, json=payload, impersonate='chrome')
        data = resp.json()

        return data.get('RESPONSE', {}).get('serviceable', False)
    except Exception as e:
        error_message = str(e)
        print(f"Serviceability Error for {pincode}: {e}")
        return False
    finally:
        save_json(
            data if data is not None else {
                "pincode": pincode,
                "latitude": latitude,
                "longitude": longitude,
                "error": error_message,
                "source": "serviceability"
            },
            RESPONSE1_DIR,
            f"serviceability_{pincode}.json"
        )


def get_update_ud(data):
    geolocation = {'latitude': data['latitude'], 'longitude': data['longitude']}
    addressinfo = {
        'addressLine1': data.get('locality') or data.get('location', ''),
        'city': data.get('city', ''),
        'state': data.get('state', 'Gujarat'),
        'pincode': data['pincode']
    }

    payload = {
        'geoLocation': geolocation,
        'addressInfo': addressinfo,
        'redirectionUrl': data.get('redirectionUrl', '/'),
        'marketplace': 'HYPERLOCAL',
    }

    # # Add stable T cookie
    # cookies = {
    #     'T': 'TI177933661468500173435932803269825701101039989581984531524343248229',
    # }

    try:
        response = requests.post(
            'https://2.rome.api.flipkart.com/api/4/location/update',
            headers=HEADERS,
            # cookies=cookies,
            json=payload,
            impersonate='chrome'
        )

        print(f"Update Status [{data['pincode']}]: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Update failed: {response.text[:300]}")
            return None

        # === curl_cffi compatible way to get cookies ===
        cookies_dict = {}
        set_cookie = response.headers.get('Set-Cookie', '')
        
        if set_cookie:
            for cookie_str in set_cookie.split(','):
                if '=' in cookie_str:
                    key = cookie_str.strip().split('=')[0]
                    value = cookie_str.split('=', 1)[1].split(';')[0]
                    cookies_dict[key] = value

        ud = cookies_dict.get('ud')

        if ud:
            print(f"✅ UD extracted: {ud[:60]}...")
            save_json({"cookies": cookies_dict, "ud": ud}, UPDATE_DIR, f"update_{data['pincode']}.json")
            return ud
        else:
            print("❌ UD not found in Set-Cookie header")
            print("Set-Cookie header:", set_cookie[:500])
            return None

    except Exception as e:
        print(f"❌ get_update_ud error: {e}")
        return None

def process_pincode_for_deliverability(record: Dict):
    record_id = record['id']
    pincode = record['pincode']
    location = record.get('location')   # Make sure this is captured early

    print(f"🔍 Processing pincode: {pincode} | Record ID: {record_id}")

    geo = get_lat_long_from_pincode(pincode)
    
    if geo is None or isinstance(geo, dict) and geo.get("error"):
        print(f"❌ Geocoding failed for {pincode}")
        print(f"   Error: {geo.get('error') if isinstance(geo, dict) else 'Unknown error'}")
        db_handler.update_status_pincode('pincodes', record_id, "failed")
        return

    print(f"✅ Geocoded: {geo.get('city')} | {geo.get('latitude')}, {geo.get('longitude')}")

    is_serviceable = check_serviceability(geo['latitude'], geo['longitude'], pincode)
    print(f"   Serviceable: {is_serviceable}")

    if is_serviceable:
        ud = get_update_ud(geo)          # ← Removed full_cookies for now
        if ud is None:
            print(f"❌ Failed to get UD for {pincode}")
            db_handler.update_status_pincode('pincodes', record_id, "failed")
            return
        try:
            db_handler.insert_deliverable_pincode(
                pincode=pincode,
                ud=ud,
                lat=geo['latitude'],
                lng=geo['longitude'],
                city=geo.get('city'),
                state=geo.get('state'),
                locality=geo.get('locality'),
                location=location
            )
            db_handler.update_status_pincode('pincodes', record_id, "done")    
            print(f"✅ Successfully inserted {pincode} into final_pincode_deliverable")
        except Exception as e:
            print(f"❌ Insert Error for {pincode}: {e}")
            db_handler.update_status_pincode('pincodes', record_id, "failed")
    else:
        print(f"❌ Not serviceable: {pincode}")
        db_handler.update_status_pincode('pincodes', record_id, "not_serviceable")



def fetch_product_details(pageuri: str, pincode: str, ud: str) -> Dict:
    data = None
    error_message = None
    cookies = {
        'T': 'TI177933813735000087741217135396657343599418698600319723431969621358',
        'ud': ud, 
    }
    params = {
        'cacheFirst': 'false',
    }

    json_data = {
        'pageUri': pageuri,
        'pageContext': {
            'trackingContext': {
                'context': {
                    'eVar51': 'direct_browse',
                    'eVar61': 'direct_browse',
                },
            },
            'networkSpeed': 10000,
        },
        'locationContext': {
            'pincode': pincode,
            'changed': False,
        }
    }
    # print(json.dumps(json_data, indent=2))
    data=None
    try:
        response = requests.post(
            'https://2.rome.api.flipkart.com/api/4/page/fetch',
            params=params,
            cookies=cookies,
            headers=HEADERS,
            json=json_data,
        ) 

        print(response)
        data = response.json()
        pageData= data.get('RESPONSE', {}).get('pageData', {})

        if not pageData:
            return {"error": "NOT_FOUND"}
        
        # === Safe schema extraction ===
        schema_list = pageData.get('seoData', {}).get('schema', [])
        
        if len(schema_list) > 0:
            schema = schema_list[0]
        else:
            return {
                'error':"NOT_FOUND"
            }
            
        parse_data = parse_json_file(data)

        context = data.get('RESPONSE', {}).get('pageData', {}).get('pageContext', {})
        pls = context.get('fdpEventTracking', {}) \
                             .get('events', {}) \
                             .get('psi', {}) \
                             .get('pls', {})
        
        if pls.get("unserviceabilityReason"):
            availability = "OUT_OF_STOCK"
        else:
            availability = pls.get('availabilityStatus')

        stock_status = "YES" if availability == 'IN_STOCK' else "NO"
        product_name= f"{schema.get('name')} {parse_data.get('specifications', {}).get('Net Quantity')}"

        return {
            "sku": schema.get('sku'),
            "product_name": product_name,
            "brand": schema.get('brand', {}).get('name'),
            "stock_avaliblity_status": stock_status,
            "product_data": parse_data,
            "pls":pls
        }

    except Exception as e:
        error_message = str(e)
        print(f"Product Fetch Error for pin {pincode}: {e}")
        return {}
    
    finally:
        # === Safe save in finally ===
        try:
            # Better PID extraction
            pid = None
            if pageuri and '?' in pageuri:
                query = pageuri.split('?', 1)[1]
                params = parse_qs(query)
                pid = params.get('pid', [None])[0]
            save_json(
                data if data is not None else {
                    "pageUri": pageuri,
                    "pincode": pincode,
                    "error": error_message,
                    "source": "product_details"
                },
                RESPONSE2_DIR,
                f"product_{pincode}_{pid or 'unknown'}.json"
            )
        except Exception as save_err:
            print(f"Failed to save response for pin {pincode}: {save_err}")    

# ======================= MAIN WORKER (Product Scraping) =======================
def process_record(record: Dict):
    record_id = record['id']
    url = record['product_url']
    pincode = record['pincode']
    ud=record['ud']
    state=record['state']

    if "http" in url:
        url = url.split("flipkart.com")[-1]
    
    p_url=url.split("&shop")[0]
    try:
        print(f"Processing → {p_url} | Pin: {pincode}")

        # Fetch from deliverable table instead of re-checking
        prod_data = fetch_product_details(url, pincode,ud)
        if prod_data.get('error'):
            print("%"* 50)
            print(f"❌Error fetching product details for {pincode}:{p_url}: {prod_data['error']}")
            print("%"* 50)
            db_handler.update_status("master_product_pincode", record_id, prod_data['error'])
            return
        
        result = {
            "sku": prod_data.get('sku'),
            "url": record['product_url'],
            "pincode": pincode,
            "locality": record.get('locality'),  # from deliverable table
            "city": record.get('city'),          # from deliverable table
            "state": state,        # from deliverable table
            "product_name": prod_data.get('product_name'),
            "brand": prod_data.get('brand'),
            "stock_avaliblity_status": prod_data.get('stock_avaliblity_status'),
            "EAN_code": record.get('EAN_Code'),  # from products_urls table
            "product_data": prod_data.get('product_data'),
            "pls":prod_data.get("pls")
        }

        try:
            db_handler.insert_product_data(result)
        except Exception as db_err:
            print(f"❌ Insert failed: {db_err}")
            db_handler.update_status("master_product_pincode", record_id, "failed")
            return
        db_handler.update_status("master_product_pincode", record_id, "done")
        # db_handler.insert_product_data(result)
        # print(f"✅Saved to DB: {p_url} | Pin: {pincode}")

    except Exception as e:
        print(f"❌Error processing {pincode}:{p_url}: {e}")
        db_handler.update_status("master_product_pincode", record_id, "failed")


# ======================= MAIN =======================
def main():
    db_handler.create_tables()

    print("=== Step 1: Checking Pincode Deliverability ===")
    while True:
        unique_pincode_rows = db_handler.get_unique_pending_pincodes()
        if not unique_pincode_rows:
            print("No new pincodes to check.")
            break

        print(f"Found {len(unique_pincode_rows)} unique pincodes to check.")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_pincode_for_deliverability, record) for record in unique_pincode_rows]
            for future in as_completed(futures):
                future.result()

    # print("\n=== Step 2: Creating Master Table ===\n")
    # db_handler.create_master_table()

    print("\n=== Step 3: Starting Product Scraping (Only Deliverable Pincodes) ===\n")

    while True:
        pending = db_handler.get_deliverable_pincodes()
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