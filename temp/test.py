# import json
# import os
# from curl_cffi import requests
# # from parser import *

# def request_1(latitude=22.8147446, longitude= 74.2531465):
#     url = 'https://1.rome.api.flipkart.com/api/1/location/serviceability'
#     params = None
#     headers = {
#         'Accept': '*/*',
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Cache-Control': 'no-cache',
#         'Connection': 'keep-alive',
#         'Content-Type': 'application/json',
#         'Origin': 'https://www.flipkart.com',
#         'Pragma': 'no-cache',
#         'Referer': 'https://www.flipkart.com/',
#         'Sec-Fetch-Dest': 'empty',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Site': 'same-site',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
#         'X-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36 FKUA/website/41/website/Desktop',
#         'flipkart_secure': 'true',
#         'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#     }
#     payload = {
#         'latitude': latitude,
#         'longitude': longitude,
#     }

#     response = requests.request(method='POST', url=url, params=params, headers=headers, json=payload, impersonate='chrome')
#     response.raise_for_status()

#     print(response)

#     content_type = response.headers.get('content-type', '').lower()
#     response_folder = 'pagesaves'
#     os.makedirs(response_folder, exist_ok=True)

#     if response.status_code == 200:
#         response_file = os.path.join(response_folder, 'request_1_response.json')
#         with open(response_file, 'w', encoding='utf-8') as f:
#             json.dump(response.json(), f, indent=2, ensure_ascii=False)
        

#     # return request_1_parser(response)

# def do_requests():

#     request_1_response = request_1()

# if __name__ == '__main__':
#     do_requests()


import json
import os
from curl_cffi import requests
# from parser import *

def request_1(locationcontext={'pincode': '230001'}, marketplacecontext={'marketplace': 'HYPERLOCAL'}):
    url = 'https://2.rome.api.flipkart.com/api/3/marketplace/serviceability'
    params = None
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
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
        'X-User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 FKUA/website/42/website/Desktop',
        'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'T=TI177193051592500108100310423094531036956455118585140618128981427018; K-ACTION=null; vw=1920; dpr=1; rt=null; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3ODA0MDgwODUsImlhdCI6MTc3ODY4MDA4NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZjViZTUwN2QtNGYzOS00MWY2LWEzMDUtN2JkMTNjNmI0ZjE0IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzcxOTMwNTE1OTI1MDAxMDgxMDAzMTA0MjMwOTQ1MzEwMzY5NTY0NTUxMTg1ODUxNDA2MTgxMjg5ODE0MjcwMTgiLCJrZXZJZCI6IlZJODUxNDA5NTAzQ0JENEU3Mjg2NjlEM0NBNTNDM0M1MzYiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjN9.gjHorXUKvhXZoCLWaUBITiLOQQtqh5x6DdPfXTBSJc8; Network-Type=4g; vh=945; vd=VI851409503CBD4E728669D3CA53C3C536-1771930519700-4.1778834267.1778832559.151541542; AMCVS_17EB401053DAF4840A490D4C%40AdobeOrg=1; AMCV_17EB401053DAF4840A490D4C%40AdobeOrg=-227196251%7CMCIDTS%7C20589%7CMCMID%7C10799054206039868633353306468551813230%7CMCAAMLH-1779284966%7C12%7CMCAAMB-1779439077%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1778841477s%7CNONE%7CMCAID%7CNONE; ud=1.Sf6wmi1txOQ-py5AqyL1KkuWvkCW7BYMhaBZfS7fpwCFpH1CBhxS1LMIkrOaIh1ZN1ScJMipEVN0HmHr5UxcykNKWK7fre7FpUqcPf92Qu6GjDw2lT1q2BuQANWV45vSkW35BWFGsZEYl84Y9c6JDTUnLITVYJChBMP57iBGLL9mlvjtnFf-RpXj__SVE3O9dxDesLoWldhqiFY5QVWNH7AdNK1IDADdzHcG5vAUK4v4TpA5jrzLdmxOWhonKj_z5O8yeuU5eczn7s7Adgjkc7gYheq6LPXTq_mA7cX6xHoffufqIW4nCJSGIxSRj_jptktoNBz3t7ohjOOUGsMxWwHRbiEeoWimFsOQXR-CB7XPF65A9EkPr4qPLsrLPG_8J01FUdjSmz644zwckpIcibb6IhCoTNHylHam9VWhUdIuMFIihwikYcQuCWlUKXmxVM4dj1uehCmRq5apFtOq3REpZTs6QUiRMtgo8HNCjkmTUjPCvx6Wbaa3FMQyf6AFj5tu_sni9szyHKlTKOQWXoejltWbzbOkuO4xkjB9fDzZglmje9Dn5tozrfs6ZYEz; S=d1t16Gz8aWD8/anAyYiwyNT0/TzRAU/AeXTHiw3cVRj3gvT7xN2HOTfrh3DzhgKi/gjLnfNRnjVZEMBeixS2kfo8IYw==; SN=VI851409503CBD4E728669D3CA53C3C536.TOKEF07EFC0D5F94172903F98FD3018A662.1778834284277.LO; s_sq=flipkart-prd%3D%2526pid%253Dwww.flipkart.com%25253Asearch%2526pidt%253D1%2526oid%253DfunctionJr%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DDIV; S=d1t16Pz9dPz8/Tj8/Aj8/PzYuP5WDwsd+LWTvRU9YdcrCkC2YNeckmdIN3XA47lhxPfVfyFtIEgkHj+PQe56IDMgEDw==; SN=VI851409503CBD4E728669D3CA53C3C536.TOKFD9A0F4C80014012BEB90ED41C6425BC.1778834498493.LO; at=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImQ2Yjk5NDViLWZmYTEtNGQ5ZC1iZDQyLTFkN2RmZTU4ZGNmYSJ9.eyJleHAiOjE3ODA0MDgwODUsImlhdCI6MTc3ODY4MDA4NSwiaXNzIjoia2V2bGFyIiwianRpIjoiZjViZTUwN2QtNGYzOS00MWY2LWEzMDUtN2JkMTNjNmI0ZjE0IiwidHlwZSI6IkFUIiwiZElkIjoiVEkxNzcxOTMwNTE1OTI1MDAxMDgxMDAzMTA0MjMwOTQ1MzEwMzY5NTY0NTUxMTg1ODUxNDA2MTgxMjg5ODE0MjcwMTgiLCJrZXZJZCI6IlZJODUxNDA5NTAzQ0JENEU3Mjg2NjlEM0NBNTNDM0M1MzYiLCJ0SWQiOiJtYXBpIiwidnMiOiJMTyIsInoiOiJIWUQiLCJtIjp0cnVlLCJnZW4iOjN9.gjHorXUKvhXZoCLWaUBITiLOQQtqh5x6DdPfXTBSJc8; rt=null; ud=1.Sf6wmi1txOQ-py5AqyL1KkuWvkCW7BYMhaBZfS7fpwCFpH1CBhxS1LMIkrOaIh1ZN1ScJMipEVN0HmHr5UxcykNKWK7fre7FpUqcPf92Qu6GjDw2lT1q2BuQANWV45vSkW35BWFGsZEYl84Y9c6JDTUnLITVYJChBMP57iBGLL9mlvjtnFf-RpXj__SVE3O9dxDesLoWldhqiFY5QVWNH7AdNK1IDADdzHcG5vAUK4v4TpA5jrzLdmxOWhonKj_z5O8yeuU5eczn7s7Adgjkc7gYheq6LPXTq_mA7cX6xHoffufqIW4nCJSGIxSRj_jptktoNBz3t7ohjOOUGsMxWwHRbiEeoWimFsOQXR-CB7XPF65A9EkPr4qPLsrLPG_8J01FUdjSmz644zwckpIcibb6IhCoTNHylHam9VWhUdIuMFIihwikYcQuCWlUKXmxVM4dj1uehCmRq5apFtOq3REpZTs6QUiRMtgo8HNCjkmTUjPCvx6Wbaa3FMQyf6AFj5tu_sni9szyHKlTKOQWXoejltWbzbOkuO4xkjB9fDzZglmje9Dn5tozrfs6ZYEz; vd=VI851409503CBD4E728669D3CA53C3C536-1771930519700-4.1778834498.1778832559.151623471',
    }
    payload = {
        'locationContext': locationcontext,
        'marketplaceContext': marketplacecontext,
    }

    response = requests.request(method='POST', url=url, params=params, headers=headers, json=payload, impersonate='chrome')
    response.raise_for_status()

    print(response)

    content_type = response.headers.get('content-type', '').lower()
    response_folder = 'pagesaves'
    os.makedirs(response_folder, exist_ok=True)

    if response.status_code == 200:
        response_file = os.path.join(response_folder, 'request_1_response.json')
        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)
    

def do_requests():
    request_1_response = request_1()

if __name__ == '__main__':
    do_requests()
