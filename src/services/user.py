import json
from src.bot.utils.utils import verify_telegram_init_data
from src.models.user import User
from src.repositories.user import UserRepository
from src.services.auth_service import AuthService


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, name: str, email: str, password: str, init_data: str = None) -> User:
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User already exists")

        hashed_password = AuthService.hash_password(password)
        user = User(
            name=name,
            email=email,
            password=hashed_password,
        )

        if init_data:
            try:
                data = verify_telegram_init_data(init_data)
                telegram_user = json.loads(data["user"])
                user.telegram_id = str(telegram_user["id"])
                user.telegram_username = telegram_user.get("username")
            except Exception as e:
                raise ValueError(f"Invalid telegram data: {str(e)}")

        return self.user_repository.add(user)

    def login(self, email: str, password: str, init_data: str = None) -> str:
        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not AuthService.verify_password(password, user.password):
            raise ValueError("Invalid credentials")
        
        if init_data and not user.telegram_id:
            from src.bot.utils.utils import verify_telegram_init_data
            import json
            try:
                data = verify_telegram_init_data(init_data)
                telegram_user = json.loads(data["user"])
                user.telegram_id = str(telegram_user["id"])
                user.telegram_username = telegram_user.get("username")
                self.user_repository.update(user)
            except Exception:
                pass # Don't block login if telegram linking fails

        return AuthService.create_access_token(data={"sub": str(user.id)})

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