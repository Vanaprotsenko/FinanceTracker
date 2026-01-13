import uuid
from fastapi import Depends, APIRouter, HTTPException, status
from src.db.database import get_db
from src.repositories.record import RecordRepository
from src.schemas.record import RecordBase, RecordUpdate, RecordCreate, RecordDelete, RecordRead
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
    return service.list_records(user_id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RecordRead)
async def create_record(
        record: RecordCreate,
        user_id: uuid.UUID = Depends(get_current_user_id),
        db: Session = Depends(get_db)
):
    repository = RecordRepository(db)
    service = RecordService(repository)
    record = service.create_record(user_id, record)

    return {"record": record, "currency":record.currency, "amount":record.amount, "type":record.type, "description":record.description}

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
        
    return {"amount": record.amount, "description": record.description}

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
    type: str, 
    description: str, 
    currency: str, 
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_db)
):
    repository = RecordRepository(session)
    service = RecordService(repository)
    
    # Check if record exists and belongs to user
    record = service.read_records(record_id)
    if not record or record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
        
    updated_record = service.update_record(record_id, user_id=user_id, amount=amount, type=type, description=description, currency=currency)
    return {"id": updated_record.id}