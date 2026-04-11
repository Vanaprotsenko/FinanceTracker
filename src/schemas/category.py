import uuid
from pydantic import BaseModel
from typing import Optional


class CategoryRead(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        orm_mode = True
