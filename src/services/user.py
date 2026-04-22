from src.models.user import User
from src.repositories.user import UserRepository
from src.services.auth_service import AuthService


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(
            self,
            name: str,
            email: str,
            password: str,
            telegram_id=None
    ) -> User:
        telegram_id = str(telegram_id).strip() if telegram_id is not None else None
        if telegram_id == "":
            telegram_id = None

        existing_user = self.user_repository.get_by_email(email)
        existing_tg_user = self.user_repository.get_by_telegram_id(telegram_id) if telegram_id else None

        if existing_tg_user and (not existing_user or existing_tg_user.id != existing_user.id):
            raise ValueError("Telegram account is already linked to another user")

        if existing_user:
            if telegram_id and not existing_user.telegram_id:
                existing_user.telegram_id = str(telegram_id)
                return self.user_repository.update(existing_user)
            raise ValueError("User already exists")

        hashed_password = AuthService.hash_password(password)
        user = User(
            name=name,
            email=email,
            password=hashed_password,
            telegram_id=str(telegram_id) if telegram_id is not None else None
        )

        return self.user_repository.add(user)

    def login(self,email: str,password: str,telegram_id: str | None = None) -> str:

        telegram_id = str(telegram_id).strip() if telegram_id is not None else None
        if telegram_id == "":
            telegram_id = None

        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not AuthService.verify_password(password, user.password):
            raise ValueError("Invalid credentials")

        if telegram_id:
            linked_user = self.user_repository.get_by_telegram_id(telegram_id)
            if linked_user and linked_user.id != user.id:
                raise ValueError("Telegram account is already linked to another user")
            if not user.telegram_id:
                user.telegram_id = str(telegram_id)
                self.user_repository.update(user)

        return AuthService.create_access_token(data={"sub": str(user.id)})

    def verify_user_by_telegram(self, telegram_id: str):
        user = self.user_repository.get_by_telegram_id(telegram_id)

        if not user:
            raise ValueError("User by telegram id not found")

        return self.user_repository.get_by_telegram_id(telegram_id)

    def read_user(self, email: str) -> User:
        return self.user_repository.read(email)

    def delete_user(self, email: str) -> User:
        user = self.user_repository.delete(email)

        if not user:
            raise ValueError("User doesn't exist")

        return user

    def update_user(self, email: str, name: str, password: str) -> User:
        user = self.user_repository.get_by_email(email)

        if not user:
            raise ValueError("User not found")

        user.name = name
        user.password = AuthService.hash_password(password)

        return self.user_repository.update(user)