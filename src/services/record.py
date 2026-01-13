import uuid
from src.models.record import Record
from src.repositories.record import RecordRepository
from src.schemas.record import RecordCreate


class RecordService:
    def __init__(self, record_repository: RecordRepository):
        self.record_repository = record_repository

    def create_record(self, user_id: uuid.UUID, data: RecordCreate) -> Record:
        record = Record(
            id=uuid.uuid4(),
            user_id=user_id,
            amount=data.amount,
            type=data.type,
            description=data.description,
            currency=data.currency,
        )
        return self.record_repository.add(record)

    def list_records(self, user_id: uuid.UUID) -> list[Record]:
        return self.record_repository.get_all_for_user(user_id)

    def read_records(self, record_id):
        return self.record_repository.read(record_id)

    def update_record(self, record_id, user_id, amount, type, description, currency) -> Record:
        record = self.record_repository.read(record_id)

        if not record:
            raise ValueError("Record not found")

        record.user_id = user_id
        record.amount = amount
        record.type = type
        record.description = description
        record.currency = currency
        
        return self.record_repository.update(record)

    def delete_record(self, record_id) -> Record:
        record = self.record_repository.delete(record_id)

        if not record:
            raise ValueError("The record doesn't exist")

        return record