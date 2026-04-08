from src.models.user import User
from src.repositories.base import Repository


class UserRepository(Repository):
    def __init__(self, session):
        self.session = session

    def get_by_email(self, email: str) -> User:
        return self.session.query(User).filter_by(email=email).first()

    def get_by_id(self, id: int) -> User:
        return self.session.query(User).filter_by(id=id).first()

    def add(self, user: User):
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def read(self, email: str):
        return self.get_by_email(email)

    def delete(self, email: str):
        user = self.get_by_email(email)

        if not user:
            return None

        self.session.delete(user)
        self.session.commit()
        return user

    def get_by_telegram_id(self, telegram_id: str) -> User:
        return self.session.query(User).filter_by(telegram_id=str(telegram_id)).first()

    def update(self, user: User) -> User:
        self.session.commit()
        self.session.refresh(user)
        return user

