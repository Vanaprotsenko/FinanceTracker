from fastapi import Depends, APIRouter, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, ReadUser, Token, UserLogin
from src.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=ReadUser)
async def signup(
    user_in: UserCreate,
    session: Session = Depends(get_db)
):
    repository = UserRepository(session)
    service = UserService(repository)

    try:
        user = service.create_user(user_in.name, user_in.email, user_in.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    session: Session = Depends(get_db)
):
    repository = UserRepository(session)
    service = UserService(repository)
    
    try:
        token = service.login(login_data.email, login_data.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/tg-signup")
async def tg_login(
    user_in: UserCreate,
    telegram_id: int = Query(...),
    telegram_username: str = Query(None),
    session: Session = Depends(get_db)
):
    repository = UserRepository(session)
    service = UserService(repository)
    try:
        user = service.create_user(
            user_in.name,
            user_in.email,
            user_in.password,
            telegram_username,
            telegram_id,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

