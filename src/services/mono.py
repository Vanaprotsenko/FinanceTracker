import time
import requests
import json

MONO_TOKEN = "uYx7tn2hTySXt4fpl7y1EB2HbGnTsOTnzKXMjfpJ7Vd0"
UAN_ACCOUNT_ID = "5AwYrwUNZWwsrC0juS1T9A"

account_id_EURO = "BCB_ef7owJvv34cGVaZ7Yw"

from_ts = int(time.time()) - 7 * 24 * 3600
to_ts = int(time.time())

url = f"https://api.monobank.ua/personal/statement/{UAN_ACCOUNT_ID}/{from_ts}/{to_ts}"

resp = requests.get(url, headers={"X-Token": MONO_TOKEN})
transactions = resp.json()
with open("data_for_last_7_days.json", "w") as f:
    json.dump(transactions, f, indent=4)

print(transactions)