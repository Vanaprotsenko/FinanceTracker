import uuid
import logging
from datetime import datetime

from src.integrations.llm_service import LLMService
from src.models.record import Record
from src.repositories.record import RecordRepository
from src.repositories.category import CategoryRepository
from src.repositories.user import UserRepository
from src.schemas.record import RecordCreate


class RecordService:
    def __init__(self, record_repository: RecordRepository, category_repository: CategoryRepository = None):
        self.record_repository = record_repository
        self.category_repository = category_repository
        self.user_repository = UserRepository(record_repository.session)
        self.logger = logging.getLogger(__name__)
        self.llm_service = LLMService()

    def create_record(self, user_id: uuid.UUID, data: RecordCreate, card_id=None) -> Record:
        category_id = None
        if data.category_name and self.category_repository:
            category = self.category_repository.get_or_create(user_id, data.category_name)
            category_id = category.id

        record = Record(
            id=uuid.uuid4(),
            user_id=user_id,
            amount=data.amount,
            type=data.type or ("income" if data.amount >= 0 else "expense"),
            description=data.description,
            currency=data.currency,
            mono_card_id=card_id if card_id else data.mono_card_id,
            created_at=data.created_at,
            category_id=category_id,
        )
        return self.record_repository.add(record)

    async def create_record_from_tg(self,telegram_id: str,file_bytes,):
        user = self.user_repository.get_by_telegram_id(str(telegram_id).strip())

        if not user:
            raise ValueError("User not found for telegram_id")

        self.logger.info(f"User found: {user}")

        amount_raw = await self.llm_service.get_price_from_llm_service(file_bytes)
        tg_record = Record(
            id=uuid.uuid4(),
            user_id=user.id,
            amount=float(amount_raw),
            type="expense",
            description="Bill",
            currency="EUR",
            created_at=datetime.now()
        )
        self.logger.info(f"Record created: {tg_record}")
        return self.record_repository.add(tg_record)

    def create_records(self, user_id: uuid.UUID, records: list[RecordCreate], card_id) -> dict:
        created = 0
        skipped = 0
        for record in records:
            existing = self.record_repository.find_by_card_and_time(
                user_id, card_id, record.created_at, record.amount
            )
            if existing:
                skipped += 1
                continue
            self.create_record(user_id, record, card_id)
            created += 1
        self.logger.info(f"Records sync: {created} created, {skipped} skipped for user {user_id}")
        return {"records_created": created, "records_skipped": skipped}

    def list_records(self, user_id: uuid.UUID) -> list[Record]:
        return self.record_repository.get_all_for_user(user_id)

    def read_records(self, record_id):
        return self.record_repository.read(record_id)

    def update_record(self, record_id, user_id, amount, description, currency, created_at=None) -> Record:
        record = self.record_repository.read(record_id)

        if not record:
            raise ValueError("Record not found")

        record.user_id = user_id
        record.amount = amount
        record.description = description
        record.currency = currency
        if created_at is not None:
            record.created_at = created_at
        
        return self.record_repository.update(record)

    def delete_record(self, record_id) -> Record:
        record = self.record_repository.delete(record_id)

        if not record:
            raise ValueError("The record doesn't exist")

        return record