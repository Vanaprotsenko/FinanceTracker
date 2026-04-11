import uuid
from fastapi import Depends, APIRouter, status
from src.db.database import get_db
from src.repositories.category import CategoryRepository
from src.schemas.category import CategoryRead
from sqlalchemy.orm import Session
from src.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[CategoryRead])
async def list_categories(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Return all categories for the current user."""
    repository = CategoryRepository(db)
    return repository.get_all_for_user(user_id)
