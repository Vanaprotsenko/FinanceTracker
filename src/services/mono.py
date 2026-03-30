import time
import httpx
from datetime import datetime
from typing import Dict
import logging

from src.repositories.user import UserRepository
from src.repositories.mono import MonoRepository
from src.models.mono import MonoCards, MonoTransaction



class MonoService:
    def __init__(self, user_repository: UserRepository, mono_repository: MonoRepository):
        self.user_repository = user_repository
        self.mono_repository = mono_repository
        self.logger = logging.getLogger(__name__)

    async def get_accounts(self, user_id):
        return self.mono_repository.get_by_user_id(user_id)

    async def get_mono_token(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        return user.mono_token

    async def get_card_info(self, user_id):
        return self.mono_repository.get_all_cards_by_user_id(user_id)

    async def get_card_by_id(self, card_id):
        card = self.mono_repository.get_card_by_id(card_id)
        if not card:
            raise ValueError("The card doesn't exist")
        return card

    async def get_card_by_id_safe(self, card_id):
        return self.mono_repository.get_card_by_id(card_id)

    async def save_cards_info(self, user_id):
        token = await self.get_mono_token(user_id)
        await self.save_mono_cards_data(token, user_id)

    async def verify_token(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        if user.mono_token:
            return True
        return False

    async def save_token(self, user_id, mono_token: str):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.mono_token = mono_token
        return self.user_repository.update(user)

    async def get_transactions_by_card_id(self, card_id):
        card = self.mono_repository.get_card_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")
        return self.mono_repository.get_all_transaction_by_card_id(card.id)

    async def update_card_name(self, card_id, new_card_name: str):
        card = self.mono_repository.get_card_by_id(card_id)
        if not card:
            raise ValueError("The card doesn't exist")

        card.mono_card_name = new_card_name
        return self.mono_repository.update_card(card)

    async def save_mono_cards_data(self, token: str, user_id):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.monobank.ua/personal/client-info",
                headers={"X-Token": token}
            )

        resp.raise_for_status()
        raw_data = resp.json()

        self.logger.info(f"The data received from endpoint client-info {raw_data}")

        new_cards_added = 0

        for item in raw_data["accounts"]:
            card_id = item.get("id")
            existing_card = await self.get_card_by_id_safe(card_id)
            if existing_card:
                continue

            mono_accounts_info = MonoCards(
                user_id=user_id,
                card_id=card_id,
                currency_code=item.get("currencyCode"),
                balance=item.get("balance"),
            )
            self.mono_repository.add(mono_accounts_info)
            new_cards_added += 1

        if new_cards_added == 0:
            raise ValueError("All your Mono cards are already synced.")

        self.logger.info(f"Successfully saved {new_cards_added} new accounts for client with name {raw_data['name']}")
        return f"Successfully saved {new_cards_added} new accounts for client with name {raw_data['name']}"

    async def sync_card(self, card_id: str, user_id) -> dict:
        """
        Single sync operation: fetch from Mono API → dedup mono_transactions → update balance.
        Returns a dict with counts of new/skipped transactions.
        """
        card = self.mono_repository.get_card_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")

        # 1. Fetch last 30 days from Mono API
        raw_data = await self._fetch_transactions(card_id, user_id)

        # 2. Save new MonoTransactions with deduplication
        new_mono_txns = []
        skipped = 0
        for item in raw_data:
            tx_time = datetime.fromtimestamp(item.get("time"))
            tx_amount = item.get("amount")
            tx_desc = item.get("description", "")

            existing = self.mono_repository.find_transaction(
                card.id, tx_time, tx_amount, tx_desc
            )
            if existing:
                skipped += 1
                continue

            mono_tx = MonoTransaction(
                card_id=card.id,
                time=tx_time,
                description=tx_desc,
                amount=tx_amount,
                operationAmount=item.get("operationAmount"),
                currency=item.get("currencyCode"),
            )
            self.mono_repository.add(mono_tx)
            new_mono_txns.append(mono_tx)
            self.logger.info(f"Saved new mono transaction: {tx_desc} ({tx_amount}) at {tx_time}")

        # 3. Update card balance
        await self._update_card_balance(card, user_id)

        self.logger.info(
            f"Sync complete for card {card_id}: "
            f"{len(new_mono_txns)} new, {skipped} skipped, {len(raw_data)} total fetched"
        )

        return {
            "new_transactions": len(new_mono_txns),
            "skipped_duplicates": skipped,
            "total_fetched": len(raw_data),
            "mono_transactions": new_mono_txns,
            "card_id": card_id,
        }

    async def save_transaction(self, card_id, user_id):
        """Legacy method - kept for backward compatibility but now uses sync_card."""
        result = await self.sync_card(card_id, user_id)
        return f"Successfully saved {result['new_transactions']} transactions for card {card_id} ({result['skipped_duplicates']} duplicates skipped)"

    async def _update_card_balance(self, card, user_id):
        """Refresh card balance from Mono API."""
        try:
            token = await self.get_mono_token(user_id)
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.monobank.ua/personal/client-info",
                    headers={"X-Token": token}
                )
            resp.raise_for_status()
            raw_data = resp.json()

            for account in raw_data.get("accounts", []):
                if account.get("id") == card.card_id:
                    self.mono_repository.update_card_balance(card, account.get("balance", card.balance))
                    self.logger.info(f"Updated balance for card {card.card_id}: {account.get('balance')}")
                    break
        except Exception as e:
            self.logger.warning(f"Failed to update card balance: {e}")

    async def _fetch_transactions(self, card_id: str, user_id) -> Dict:
        from_ts = int(time.time()) - 30 * 24 * 3600  # the last 30 days
        to_ts = int(time.time())

        token = await self.get_mono_token(user_id)

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.monobank.ua/personal/statement/{card_id}/{from_ts}/{to_ts}",
                headers={"X-Token": token}
            )

        resp.raise_for_status()
        return resp.json()

    async def delete_card(self, card_id):
        card = self.mono_repository.get_card_by_id(card_id)

        if not card:
            raise ValueError("The card doesn't exist")

        self.mono_repository.delete(card_id)
        return f"The card with id {card_id} was successfully deleted"

