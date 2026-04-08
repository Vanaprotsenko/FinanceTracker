import json
from src.repositories.user import UserRepository
from src.bot.utils.utils import verify_telegram_init_data
from fastapi import Depends, APIRouter, HTTPException, status
from src.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/auth/telegram/login")
def telegram_login(init_data: str, session: Session = Depends(get_db)):
    repository = UserRepository(session)
    from src.bot.utils.utils import verify_telegram_init_data
    from src.services.auth_service import AuthService
    
    try:
        data = verify_telegram_init_data(init_data)
        telegram_user = json.loads(data["user"])
        telegram_id = str(telegram_user["id"])
        
        user = repository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not linked")
            
        token = AuthService.create_access_token(data={"sub": str(user.id)})
        
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/auth/telegram/init")
def telegram_init(init_data: str, session: Session = Depends(get_db)):
    repository = UserRepository(session)
    try:
        data = verify_telegram_init_data(init_data)
        telegram_user = json.loads(data["user"])
        telegram_user_id = str(telegram_user["id"])
        user = repository.get_by_telegram_id(telegram_user_id)
        return {"linked": bool(user)}
    except Exception:
        return {"linked": False}

@router.get("/auth/telegram/user/{telegram_id}")
def get_telegram_user(telegram_id: str, session: Session = Depends(get_db)):
    repository = UserRepository(session)
    user = repository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"email": user.email, "name": user.name}
