import uuid
from pydantic import BaseModel

class RecordBase(BaseModel):
    amount: float
    currency: str
    description: str

class RecordCreate(RecordBase):
    class Config:
        orm_mode = True

class RecordResponse(BaseModel):
    id: uuid.UUID

class RecordRead(RecordBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class RecordUpdate(BaseModel):
    id: uuid.UUID

class RecordDelete(BaseModel):
    id: uuid.UUID