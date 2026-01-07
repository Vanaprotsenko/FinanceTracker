from fastapi import Depends, APIRouter

from src.dependencies import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserBase
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/create",status_code=200, response_model=UserCreate)
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = User(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user