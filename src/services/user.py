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
            telegram_username=None,
            telegram_id=None
    ) -> User:

        existing_user = self.user_repository.get_by_email(email)
        existing_tg_user = self.user_repository.get_by_telegram_id(telegram_id)

        if existing_user or existing_tg_user:
            raise ValueError("User already exists")

        hashed_password = AuthService.hash_password(password)
        user = User(
            name=name,
            email=email,
            password=hashed_password,
            telegram_username=telegram_username,
            telegram_id=telegram_id
        )

        return self.user_repository.add(user)

    def login(self, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not AuthService.verify_password(password, user.password):
            raise ValueError("Invalid credentials")

        return AuthService.create_access_token(data={"sub": str(user.id)})

    def login_user_tg(self, telegram_id: str, telegram_username: str) -> str:
        user = self.user_repository.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("User not found")

        if not AuthService.verify_password(password, user.password):
            raise ValueError("Invalid credentials")

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