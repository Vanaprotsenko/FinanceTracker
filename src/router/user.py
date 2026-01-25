from fastapi import Depends, APIRouter, HTTPException, status
from src.db.database import get_db
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, ReadUser, Token, UserLogin
from sqlalchemy.orm import Session
from src.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=ReadUser)
async def signup(
        user_in: UserCreate,
        password: str, # Keeping it simple for now as per current structure, but usually it's in UserCreate
        session: Session = Depends(get_db)
):
    repository = UserRepository(session)
    service = UserService(repository)

    try:
        user = service.create_user(user_in.name, user_in.email, password, user_in.init_data)
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
        token = service.login(login_data.email, login_data.password, login_data.init_data)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))