import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from curl_cffi import requests
from datetime import datetime

# ==================== CONFIG ====================
RESPONSE_FOLDER = 'pagesaves'
SAVE_RESPONSE = True
REQUEST_TIMEOUT = 15

os.makedirs(RESPONSE_FOLDER, exist_ok=True)


def request_1(
    pincode: int,
    cachefirst='false',
    pageuri='/milky-mist-plain-pouch-curd/p/itmb9f328ac066d3?pid=CUYGK2CDY5FDC8ZS&lid=LSTCUYGK2CDY5FDC8ZSXGAKI6&marketplace=HYPERLOCAL',
    pagecontext=None,
    locationcontext=None
):
    """Single Flipkart blocking check request"""
    
    if pagecontext is None:
        pagecontext = {'trackingContext': {}, 'networkSpeed': 10000}
    
    if locationcontext is None:
        locationcontext = {'pincode': pincode, 'changed': False}

    url = 'https://1.rome.api.flipkart.com/api/4/page/fetch'
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': 'T=TI177372477624200140974326778506532267306020560269982940774322126482; vw=1600; dpr=1.2000000476837158; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C20588%7CMCMID%7C69136679222682959801448717696275714314%7CMCAAMLH-1779364097%7C12%7CMCAAMB-1779364097%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1778766497s%7CNONE%7CMCAID%7CNONE; ULSN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjb29raWUiLCJhdWQiOiJmbGlwa2FydCIsImlzcyI6ImF1dGguZmxpcGthcnQuY29tIiwiY2xhaW1zIjp7ImdlbiI6IjEiLCJ1bmlxdWVJZCI6IlVVSTI2MDUxNDE3MTg1MDQ4N0k4MTZEUEUiLCJma0RldiI6bnVsbH0sImV4cCI6MTc5NDUzOTMzMCwiaWF0IjoxNzc4NzU5MzMwLCJqdGkiOiIxM2ViMTE4ZC1lYmFjLTRkY2ItOWFhNy0wMzI0OTQ4YTYzMjIifQ.qQ38HcrOZeQQ7PDBcLWQelPo9FY6O3ZdQRYZAHJwwkc; Network-Type=4g; vh=222; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhlM2ZhMGE3LTJmZDMtNGNiMi05MWRjLTZlNTMxOGU1YTkxZiJ9.eyJleHAiOjE3Nzg4MjUxMDUsImlhdCI6MTc3ODgyMzMwNSwiaXNzIjoia2V2bGFyIiwianRpIjoiYjFiNWI0ZDItODU1Zi00YTQxLWE3NTktOTAzYWI5MzRlMDBiIiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzczNzI0Nzc2MjQyMDAxNDA5NzQzMjY3Nzg1MDY1MzIyNjczMDYwMjA1NjAyNjk5ODI5NDA3NzQzMjIxMjY0ODIiLCJiSWQiOiJENUtPTDIiLCJrZXZJZCI6IlZJODZDRERBQkZFNkQwNDNDREExRDFBREZEQjU0RUU4MDQiLCJ0SWQiOiJtYXBpIiwiZWFJZCI6ImF4ang1cW9mMnl0b3lNajFibUNWWHYxTDh1NmtUSjBfb2YtMWE4ZDNtNmV1Q2h6WTRvVjVsUT09IiwidnMiOiJMSSIsInoiOiJDSCIsIm0iOnRydWUsImdlbiI6M30.ph_-FnJPUM_A-Q7QgpWcTZc-dKGxyUgQk46hhvLEjXM; rt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNhNzdlZTgxLTRjNWYtNGU5Ni04ZmRlLWM3YWMyYjVlOTA1NSJ9.eyJleHAiOjE3OTQ3MjA5MDUsImlhdCI6MTc3ODgyMzMwNSwiaXNzIjoia2V2bGFyIiwianRpIjoiMmQ0YjMwYzAtZGU1ZS00ZDBhLTk0ODAtZjU1NzMzMmEyOGU2IiwidHlwZSI6IlJUIiwiZElkIjoiVEkxNzczNzI0Nzc2MjQyMDAxNDA5NzQzMjY3Nzg1MDY1MzIyNjczMDYwMjA1NjAyNjk5ODI5NDA3NzQzMjIxMjY0ODIiLCJiSWQiOiJENUtPTDIiLCJrZXZJZCI6IlZJODZDRERBQkZFNkQwNDNDREExRDFBREZEQjU0RUU4MDQiLCJ0SWQiOiJtYXBpIiwibSI6eyJ0eXBlIjoibiJ9LCJ2IjoiU0NGWk5HIn0.lht4mveTtMluFS0HRgMj6LUIWK0fetzN8nKpRpVKej0; vd=VI86CDDABFE6D043CDA1D1ADFDB54EE804-1773724794031-8.1778823305.1778821375.160512024; ud=0.FdEBuBCzSytF6hYhm1RsLxJtADO-ptLBJSRTn5heKgOs8xTxr84F4mmuDn9Gq2E6kUdKyzCYwE27js9afVoy8c_H2QK0l6VDlbwd3otxo1Sn2U3vZ4wO-9La-176-kU-INZjVGPb8uuOzfDDjfBP5NWpSwu7y0n4a27FjP17qXpyRlsRo7Bm_hB175g_XNutWtrDpi73x9nrmC6yk0hx6H7cqGh2twmZs6xJg_rTe-4GeZzc53Ms3czDNWokm_9WmSflJkI427n0jEp4BReGnVXmZxVsXPR90Uv_40gcrzZZMpF8bMUm1RLJL9xFhgcXMfwZSmCC48zPbixT04f9UbllfDzDIrEptTLQv5WailVCFwbH4Hb8fR3z9iehVniX6mDRoV2rtDMZyNN3zclbskUSeCBDDW2gcTuw_28eSbwtBuDCbKcCibJEqr2le_yhNJTzGJzze-7zGbunt3jfkwwpxZH5vYVdgr0HDnJpPD3W6LWArMq6w_Y8PoI4OAj39n7hbKlOKkFT7XweH4x4v3domZzN78Y6ghrnSG1P3b3SGhyycERigh55BDntZV0Pluowb9QpTrv-WsIg2Ts1Y36qtCqRGolcO_vMIKoKexCXayBWX3CH8JqjRnlksdUySEkgIspY-Elxf2ghWUbelgFSBzX6ZCcC3pvhvCaXj4uIIR_IV8yDH8Q8hMmJ1jzFIXiULlCMoTzEJ5n1w9L_eGw5S09X6vRkJa3s2lSxLWjBRl9MSNt0HAbWa0MCPm2N; S=d1t14BD8/KVs/Pxc/EmBtPwc/V3RQqcLMmfpx97HKHp3t+pT5JoS2bYEPJrX2uMRvJXnztRXqngDUGdIoGokRI23Vrw==; SN=VI86CDDABFE6D043CDA1D1ADFDB54EE804.TOK9C0162B1F7484230A1DB261490032015.1778823315841.LI',
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
    }

    payload = {
        'pageUri': pageuri,
        'pageContext': pagecontext,
        'locationContext': locationcontext,
    }

    try:
        response = requests.request(
            method='POST',
            url=url,
            params={'cacheFirst': cachefirst},
            headers=headers,
            json=payload,
            impersonate='chrome',
            timeout=REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        print(f"✅ [{pincode}] Success")

        if SAVE_RESPONSE:
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"flipkart_{pincode}_{timestamp}.json"
            with open(os.path.join(RESPONSE_FOLDER, filename), 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=2, ensure_ascii=False)

        return {'pincode': pincode, 'status': 'success', 'response_time': datetime.now().isoformat()}

    except Exception as e:
        print(f"❌ [{pincode}] Failed | {e}")
        return {'pincode': pincode, 'status': 'error', 'error': str(e)}


def check_multiple_pincodes(pincodes: list, total_requests: int = 100, concurrent_requests: int = 8):
    """
    Send large number of requests (1000, 2000 etc.)
    """
    # Limit pincodes according to total_requests
    if total_requests < len(pincodes):
        pincodes_to_process = pincodes[:total_requests]
    else:
        pincodes_to_process = pincodes

    print(f"🚀 Starting {len(pincodes_to_process)} requests")
    print(f"🔢 Total Requests : {total_requests}")
    print(f"⚡ Concurrency    : {concurrent_requests}\n")

    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        future_to_pincode = {
            executor.submit(request_1, pincode): pincode 
            for pincode in pincodes_to_process
        }

        for future in as_completed(future_to_pincode):
            result = future.result()
            results.append(result)

    total_time = time.time() - start_time
    success = sum(1 for r in results if r.get('status') == 'success')

    print("\n" + "="*70)
    print(f"✅ FINISHED {len(results)} REQUESTS")
    print(f"⏱️  Total Time     : {total_time:.2f} seconds")
    print(f"📊 Success Rate   : {success}/{len(results)}")
    print("="*70)

    # Save summary
    summary = {
        "total_requested": total_requests,
        "actual_processed": len(results),
        "success": success,
        "failed": len(results) - success,
        "duration_seconds": round(total_time, 2),
        "results": results
    }

    with open('blocking_check_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Summary saved → blocking_check_summary.json")
    return results


# ====================== MAIN ======================
if __name__ == '__main__':
    
    # Put your full list of pincodes here
    all_pincodes = [380001, 500004, 110001, 400001, 600001, 700001, 201301, 560001] * 300  

    # ================== CHANGE THESE ==================
    results = check_multiple_pincodes(
        pincodes=all_pincodes,
        total_requests=1000,          # ← Change this (1000, 2000, 5000 etc.)
        concurrent_requests=100        # Recommended: 8–12
    )