import json

import requests


# MONO_TOKEN = "uYx7tn2hTySXt4fpl7y1EB2HbGnTsOTnzKXMjfpJ7Vd0"
#
# def get_accounts(token: str):
#     resp = requests.get(
#         "https://api.monobank.ua/personal/client-info",
#         headers={"X-Token": token}
#     )
#     resp.raise_for_status()
#     print(resp.json())
#     with open('accounts.json', 'w', encoding='utf-8') as f:
#         json.dump(resp.json(), f, indent=4)
#
# print(get_accounts(MONO_TOKEN))

with open("accounts.json") as json_file:
    accounts = json.load(json_file)


raw_data = accounts["accounts"]
result = []

for item in raw_data:
    result.append({
        "id": item["id"],
        "currencyCode": item["currencyCode"],
        "balance": item["balance"],
        "maskedPan": item["maskedPan"],
    })

# print(result)

for res in result:
    print(res)
