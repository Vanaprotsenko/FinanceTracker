import uuid
import logging
from src.models.record import Record
from src.repositories.record import RecordRepository
from src.schemas.record import RecordCreate



class RecordService:
    def __init__(self, record_repository: RecordRepository):
        self.record_repository = record_repository
        self.logger = logging.getLogger(__name__)

    def create_record(self, user_id: uuid.UUID, data: RecordCreate, card_id=None) -> Record:
        record = Record(
            id=uuid.uuid4(),
            user_id=user_id,
            amount=data.amount,
            description=data.description,
            currency=data.currency,
            mono_card_id=card_id if card_id else None
        )
        return self.record_repository.add(record)

    def create_records(self, user_id: uuid.UUID, records: list[RecordCreate], card_id) -> list[Record]:
        for record in records:
            self.create_record(user_id, record, card_id)
            self.logger.info(f"Record was succefully created for user: {user_id}")
        return self.list_records(user_id)

    def list_records(self, user_id: uuid.UUID) -> list[Record]:
        return self.record_repository.get_all_for_user(user_id)

    def read_records(self, record_id):
        return self.record_repository.read(record_id)

    def update_record(self, record_id, user_id, amount, description, currency) -> Record:
        record = self.record_repository.read(record_id)

        if not record:
            raise ValueError("Record not found")

        record.user_id = user_id
        record.amount = amount
        record.description = description
        record.currency = currency
        
        return self.record_repository.update(record)

    def delete_record(self, record_id) -> Record:
        record = self.record_repository.delete(record_id)

        if not record:
            raise ValueError("The record doesn't exist")

        return record