from src.models.record import Record
from src.repositories.base import Repository


class RecordRepository(Repository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id) -> Record:
        return self.session.query(Record).filter_by(id=id).first()

    def read(self, record_id) -> Record:
        return self.get_by_id(record_id)

    def get_all_for_user(self, user_id) -> list[Record]:
        return self.session.query(Record).filter_by(user_id=user_id).all()

    def add(self, record: Record):
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update(self, record: Record):
        self.session.commit()
        self.session.refresh(record)
        return record

    def delete(self, record_id) -> Record:
        record = self.get_by_id(record_id)

        if not record:
            return None

        self.session.delete(record)
        self.session.commit()
        return record
