import uuid
from pydantic import BaseModel,EmailStr



class UserBase(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    password: str


class UserCreate(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str

    class Config:
        from_attributes = True