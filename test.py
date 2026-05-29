# import requests

# headers = {
#     'Content-Type': 'application/json',
#     'X-Goog-Api-Key': 'AIzaSyAtKsoYaqKOXMV00f9qLDAgbYYevlxAGsQ',
# }

# json_data = {
#     'input': '560001',
#     'includedRegionCodes': [
#         'in',
#     ],
# }

# response = requests.post('https://places.googleapis.com/v1/places:autocomplete', headers=headers, json=json_data)
# with open('response.json', 'w', encoding='utf-8') as f:
#     f.write(response.text)

import requests

headers = {
    'X-Goog-Api-Key': 'AIzaSyAtKsoYaqKOXMV00f9qLDAgbYYevlxAGsQ',
    'X-Goog-FieldMask': 'id,types,addressComponents,formattedAddress,location,viewport,plusCode',
}

response = requests.get('https://places.googleapis.com/v1/places/ChIJc_E1jPQ-rjsRMhC98XQdxGY', headers=headers)
with open('response2.json', 'w', encoding='utf-8') as f:
    f.write(response.text)