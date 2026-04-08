import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class RecordBase(BaseModel):
    amount: float
    type: Optional[str] = "expense"
    currency: str
    description: str
    mono_card_id: Optional[str] = None
    created_at: Optional[datetime] = None

class RecordCreate(RecordBase):
    class Config:
        orm_mode = True

class RecordResponse(BaseModel):
    id: uuid.UUID

class RecordRead(RecordBase):
    id: uuid.UUID
    mono_card_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class RecordUpdate(BaseModel):
    id: uuid.UUID

class RecordDelete(BaseModel):
    id: uuid.UUID