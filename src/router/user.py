from fastapi import Depends, APIRouter

from src.db.database import get_db
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, ReadUser, UserDelete, UpdateUser
from sqlalchemy.orm import Session

from src.services.user import UserService

router = APIRouter()


@router.post("/users/create", status_code=200, response_model=UserCreate)
async def create_user(
        name: str,
        email: str,
        password: str,
        session: Session = Depends(get_db)
):
    repository = UserRepository(session)
    service = UserService(repository)

    user = service.create_user(name, email, password)
    return {"name": user.name, "email": user.email}

@router.get("/users/me", status_code=200, response_model=ReadUser)
async def get_current_user(email: str, session: Session = Depends(get_db)):
    repository = UserRepository(session)
    service = UserService(repository)
    user = service.read_user(email)
    return {"email": user.email, "name": user.name}

@router.delete("/user/delete", status_code=204)
async def delete_user(email: str, session: Session = Depends(get_db)):
    repository = UserRepository(session)
    service = UserService(repository)
    service.delete_user(email)

@router.patch("/users/update", status_code=200, response_model=UpdateUser)
async def update_user(name: str, email: str, password: str, session: Session = Depends(get_db)):
    repository = UserRepository(session)
    service = UserService(repository)
    user = service.update_user(name=name, email=email, password=password)
    return {"email": user.email}