import uuid
from typing import Optional
from datetime import datetime
from fastapi import Depends, APIRouter, HTTPException, status
from src.db.database import get_db
from src.repositories.record import RecordRepository
from src.repositories.category import CategoryRepository
from src.schemas.record import RecordUpdate, RecordCreate, RecordRead, RecordResponse
from sqlalchemy.orm import Session
from src.services.record import RecordService
from src.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/records", tags=["records"])

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[RecordRead])
async def list_records(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = RecordRepository(db)
    service = RecordService(repository)
    records = service.list_records(user_id)

    # Map category name from relationship into response
    result = []
    for r in records:
        data = RecordRead(
            id=r.id,
            amount=r.amount,
            type=r.type,
            currency=r.currency,
            description=r.description,
            mono_card_id=r.mono_card_id,
            created_at=r.created_at,
            category_name=r.category.name if r.category else None,
        )
        result.append(data)
    return result

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RecordResponse)
async def create_record(
    record: RecordCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = RecordRepository(db)
    category_repository = CategoryRepository(db)
    service = RecordService(repository, category_repository)
    record = service.create_record(user_id, record)

    return {"id": record.id}

@router.get("/{record_id}", status_code=200, response_model=RecordRead)
async def read_record(
    record_id: uuid.UUID, 
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    repository = RecordRepository(db)
    service = RecordService(repository)
    record = service.read_records(record_id)
    
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
        
    return RecordRead(
        id=record.id,
        amount=record.amount,
        type=record.type,
        currency=record.currency,
        description=record.description,
        mono_card_id=record.mono_card_id,
        created_at=record.created_at,
        category_name=record.category.name if record.category else None,
    )

@router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: uuid.UUID, 
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_db)
):
    repository = RecordRepository(session)
    service = RecordService(repository)
    
    # Check if record exists and belongs to user
    record = service.read_records(record_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
        
    service.delete_record(record_id)

@router.patch("/{record_id}", status_code=200, response_model=RecordUpdate)
async def update_record(
    record_id: uuid.UUID, 
    amount: float, 
    description: str, 
    currency: str,
    created_at: Optional[datetime] = None,
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_db)
):
    repository = RecordRepository(session)
    service = RecordService(repository)
    
    # Check if record exists and belongs to user
    record = service.read_records(record_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
        
    updated_record = service.update_record(record_id, user_id=user_id, amount=amount, description=description, currency=currency, created_at=created_at)

    return {"id": updated_record.id}