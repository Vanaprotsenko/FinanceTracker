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

with open("data_for_last_7_days.json") as json_file:
    data = json.load(json_file)


result = []

for item in data:
    result.append({
        "id": item["id"],
        "time": item["time"],
        "description": item["description"],
        "amount": item["amount"],
        "currencyCode": item["currencyCode"],
        "operationAmount": item["operationAmount"],
    })

# print(result)

for res in result:
    print(res)
