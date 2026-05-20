import re
from utils import RESPONSE2_DIR, save_json
from urllib.parse import parse_qs, urlparse
from lxml import html
from curl_cffi import requests
import json
from parser import parse_json_file
import os
def fetch_product_details(page_url: str, pincode: str):
    data = None
    error_message = None
    html_content = None

    try:
        # Ensure absolute URL
        if not page_url.startswith("http"):
            page_url = "https://www.flipkart.com" + page_url

        parsed = urlparse(page_url)

        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        params = parse_qs(parsed.query)

        key_params = ['pid', 'lid', 'marketplace']

        clean_params = {
            k: v[0]
            for k, v in params.items()
            if k in key_params
        }

        clean_params['pincode'] = pincode

        query_string = '&'.join(
            f"{k}={v}" for k, v in clean_params.items()
        )

        full_url = f"{base}?{query_string}"
        print(f"Scraping HTML: {full_url}")

        headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'Network-Type=4g; fonts-loaded=en_loaded; T=TI177916479980400137178317926512903013742750622557405293934159441200; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFkOTYzYzUwLTM0YjctNDA1OC1iMTNmLWY2NDhiODFjYTBkYSJ9.eyJleHAiOjE3ODA4OTI3OTksImlhdCI6MTc3OTE2NDc5OSwiaXNzIjoia2V2bGFyIiwianRpIjoiY2JlMGZiNDktZGU3ZC00ZWRjLTgyMGQtZTk0Y2YwYTgwNWVlIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzc5MTY0Nzk5ODA0MDAxMzcxNzgzMTc5MjY1MTI5MDMwMTM3NDI3NTA2MjI1NTc0MDUyOTM5MzQxNTk0NDEyMDAiLCJrZXZJZCI6IlZJNjVDRTQ4Qjc2QUQ5NDJBRDgyMTg1RTZFRUU4MUIyNjciLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJDSCIsIm0iOnRydWUsImdlbiI6M30.jvI60svPylOi1l0M6dC37DImps1lxXtfBsOVfot5-UU; K-ACTION=null; vh=200; vw=1707; dpr=1.125; isH2EnabledBandwidth=false; h2NetworkBandwidth=9; vd=VI65CE48B76AD942AD82185E6EEE81B267-1779164801212-1.1779164801.1779164801.155264867; ud=6.TgT7YT6xQBy0GgnAGjqTbXtKIzNHUjp7b0bbWFxwmVHoLkVjScgkoaz5ypRFG4AUVcgZT0jZAMWPshDJVMafFcC8xcI8ozzlTKz9r2YP7CKkYThnVLRBPnYATCJaPGC3Qy2bbtNNwFSPIdAl4tCgGp9zcAY65QLwle40XPxCuDmBtqLXB5QvsYE0aadggoOh-mpIrcqcvK0pBGamC9A5b3w7N5LJUS5iWaGV0mbd7UsHsxIj23tAqC581Kinxb_Gt2Q0ZdLuwp4OjroiZVbXsCw2Q4roCjio3-isEzw6GBUcYEIGJY6ZlBg-PoI53r4YapaaUetb-rNzsAVQfrXrUMDNEhVC9Hu7m7VYu3ORX4AaA9hA9JcfzUNx-pE0oJ278BbgOf2IewVQwscBZczEseNeWs-8NIfh34R8N0r5HV2Cj5ryBQiOX5OqjVQgHiXebL3XpGeuw9zKECbChNL0iOk7bXFznuOHEhjW3N0zQIsxkbBvcy31oGeVB8tXaQgnaT383bzWpr9uB8CafepELlYjaG3vF__LqKiVc10sknjUTyCF2JO10JPS_CH9dZhe4UyqVA9FQhRr63UMocc06w; S=d1t11Pz8QfT8/Ji8/MCk/Bz8/YU6c2LUZiGj+WghxEGSSiMAMNqtfPWmulZD5i4CayN3jt8qmcOOPDLSl2VLTGOXvYQ==; SN=VI65CE48B76AD942AD82185E6EEE81B267.TOK66F9A00D2E2742DEAD270B0855C4BACC.1779164848873.LO',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-full-version': '"148.0.7778.168"',
        'sec-ch-ua-full-version-list': '"Chromium";v="148.0.7778.168", "Google Chrome";v="148.0.7778.168", "Not/A)Brand";v="99.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"19.0.0"',
    }

        response = requests.get(full_url, headers=headers, impersonate='chrome')
        response.raise_for_status()
        html_content = response.text

        # ====================== EXTRACT INITIAL STATE ======================
        tree = html.fromstring(html_content)
        
        scripts = tree.xpath('//script[contains(text(), "__INITIAL_STATE__")]/text()')
        
        initial_state = None
        for script in scripts:
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.+?\});', script, re.DOTALL)
            if match:
                json_str = match.group(1)
                # Clean minor JS issues
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                initial_state = json.loads(json_str)
                break
            
        # data.multiWidgetState.pageDataResponse. seoData
        if not initial_state:
            return {"error": "INITIAL_STATE_NOT_FOUND"}
        data= initial_state

        multiWidgetState = data.get("multiWidgetState", {})
        pageDataResponse = multiWidgetState.get("pageDataResponse", {})
        schema_list = pageDataResponse.get('seoData', {}) \
                         .get('schema', [])
        

        if not pageDataResponse:
            return {"error": "NOT_FOUND"}

        schema_list = pageDataResponse.get('seoData', {}).get('schema', [])
        if len(schema_list) == 0:
            print("&"*50)
            print("WARNING: No schema but pageDataResponse exists")
            print(f"Schema not found in pageDataResponse for {page_url}")
            print("&"*50)
            return {"error": "NOT_FOUND"}


        schema=schema_list[0]       
        parse_data = parse_json_file(data)
        context = pageDataResponse.get('pageContext', {})
        pls = context.get('fdpEventTracking', {}) \
                             .get('events', {}) \
                             .get('psi', {}) \
                             .get('pls', {})
        
        if pls.get("unserviceabilityReason"):
            availability = "OUT_OF_STOCK"
        else:
            availability = pls.get('availabilityStatus')

        stock_status = "YES" if availability == 'IN_STOCK' else "NO"

        return {
            "sku": schema.get('sku'),
            "product_name": schema.get('name'),
            "brand": schema.get('brand', {}).get('name'),
            "stock_availability_status": stock_status,
            "product_data": parse_data,
            "pls":pls
        }

    except Exception as e:
        error_message = str(e)
        print(f"HTML Scraping Error for pin {pincode}: {e}")
        return {"error":"FAILED"}

    finally:
        # Save HTML + Parsed JSON
        pid = None
        if page_url and '?' in page_url:
            params = parse_qs(urlparse(page_url).query)
            pid = params.get('pid', [None])[0]

        save_json(
            {"data": data, "error": error_message
            },
            os.path.join(RESPONSE2_DIR, "json"),
            f"product_{pincode}_{pid or 'unknown'}"
        )
        save_json(
            {"data": html_content},
            os.path.join(RESPONSE2_DIR, "html"),
            f"product_{pincode}_{pid or 'unknown'}"
        )