from src.models.user import User
from src.repositories.user import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, name: str, email: str, password: str) -> User:
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User already exists")

        user = User(
            name=name,
            email=email,
            password=password,
        )

        return self.user_repository.add(user)

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
        user.password = password

        return self.user_repository.update(user)