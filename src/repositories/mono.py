from src.repositories.base import Repository
from src.models.mono import MonoTransaction, MonoCards


class MonoRepository(Repository):
    def __init__(self, session):
        self.session = session

    def get_by_user_id(self, user_id: str) -> MonoCards:
        return self.session.query(MonoCards).filter_by(user_id=user_id).first()

    def get_all_transaction_by_user_id(self, user_id: str) -> MonoCards:
        return self.session.query(MonoCards).filter_by(user_id=user_id).all()

    def get_card_by_id(self, card_id: str) -> MonoCards:
        return self.session.query(MonoCards).filter_by(card_id=card_id).first()

    def add(self, mono: MonoCards | MonoTransaction):
        self.session.add(mono)
        self.session.commit()
        self.session.refresh(mono)
        return mono

    def read(self, user_id):
        return self.get_by_user_id(user_id)

    def update(self, user_id):
        pass

    def delete(self, card_id):
        card = self.get_card_by_id(card_id)
        if not card:
            return None

        self.session.delete(card)
        self.session.commit()
        return card