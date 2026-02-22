import time
import requests
import json

from src.models.user import User
from src.repositories.user import UserRepository

# MONO_TOKEN = "uYx7tn2hTySXt4fpl7y1EB2HbGnTsOTnzKXMjfpJ7Vd0"
# UAN_ACCOUNT_ID = "5AwYrwUNZWwsrC0juS1T9A"
#
# account_id_EURO = "BCB_ef7owJvv34cGVaZ7Yw"
#
# from_ts = int(time.time()) - 7 * 24 * 3600
# to_ts = int(time.time())
#
# url = f"https://api.monobank.ua/personal/statement/{UAN_ACCOUNT_ID}/{from_ts}/{to_ts}"
#
# resp = requests.get(url, headers={"X-Token": MONO_TOKEN})
# transactions = resp.json()
# with open("data_for_last_7_days.json", "w") as f:
#     json.dump(transactions, f, indent=4)
#
# print(transactions)


class MonoService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def save_token(self, user_id, mono_token: str):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.mono_token = mono_token
        return self.user_repository.update(user)

