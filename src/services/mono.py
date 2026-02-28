import time
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from src.repositories.user import UserRepository
from src.repositories.mono import MonoRepository
from src.models.mono import MonoCards, MonoTransaction

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
    def __init__(self, user_repository: UserRepository, mono_repository: MonoRepository):
        self.user_repository = user_repository
        self.mono_repository = mono_repository
        self.logger = logging.getLogger(__name__)

    def save_token(self, user_id, mono_token: str):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.mono_token = mono_token
        return self.user_repository.update(user)

    def verify_token(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        if user.mono_token:
            return True
        return False

    def get_accounts(self, user_id):
        return self.mono_repository.get_by_user_id(user_id)

    def save_cards_info(self, user_id):
        token = self.get_mono_token(user_id)
        self.save_mono_cards_data(token, user_id)

    def get_mono_token(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        return user.mono_token

    def get_card_info(self, user_id):
        return self.mono_repository.get_all_cards_by_user_id(user_id)

    def save_mono_cards_data(self, token: str, user_id):
        resp = requests.get(
            "https://api.monobank.ua/personal/client-info",
            headers={"X-Token": token}
        )

        resp.raise_for_status()
        raw_data = resp.json()

        self.logger.info(f"The data received from endpoint client-info {raw_data}")

        for item in raw_data["accounts"]:
            mono_accounts_info = MonoCards(
                user_id=user_id,
                card_id=item.get("id"),
                currency_code=item.get("currencyCode"),
                balance=item.get("balance"),
            )
            self.mono_repository.add(mono_accounts_info)

        self.logger.info(f"Successfully saved accounts info for client with name {raw_data['name']}")
        return f"Successfully saved accounts info for client with name {raw_data['name']}"

    def get_transactions_by_card_id(self, card_id):
        card = self.mono_repository.get_card_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")
        return self.mono_repository.get_all_transaction_by_card_id(card.id)

    def save_transaction(self, card_id, user_id):

        card = self.mono_repository.get_card_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")

        data = self.fetch_transactions(card_id, user_id)

        for item in data:
            mono_transaction = MonoTransaction(
                card_id=card.id,
                time=datetime.fromtimestamp(item.get("time")),
                description=item.get("description"),
                amount=item.get("amount"),
                operationAmount=item.get("operationAmount"),
                currency_code=item.get("currencyCode"),
            )
            self.mono_repository.add(mono_transaction)
            self.logger.info(
                f"Successfully saved transaction for card with id {card_id} and time {item.get('time')}"
            )
        return f"Successfully saved {len(data)} transactions for card {card_id}"

    def get_card_by_id(self, card_id):
        card = self.mono_repository.get_card_by_id(card_id)

        if not card:
            raise ValueError("The card doesn't exist")

        return card

    def fetch_transactions(self, card_id: str, user_id) -> Dict:
        from_ts = int(time.time()) - 30 * 24 * 3600  # the last 30 days
        to_ts = int(time.time())

        resp = requests.get(
            f"https://api.monobank.ua/personal/statement/{card_id}/{from_ts}/{to_ts}",
            headers={"X-Token": self.get_mono_token(user_id)}
        )

        resp.raise_for_status()
        return resp.json()

    def delete_card(self, card_id):
        card = self.mono_repository.get_card_by_id(card_id)

        if not card:
            raise ValueError("The card doesn't exist")

        self.mono_repository.delete(card_id)
        return f"The card with id {card_id} was successfully deleted"

