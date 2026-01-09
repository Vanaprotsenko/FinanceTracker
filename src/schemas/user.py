from pydantic import BaseModel, EmailStr



class UserBase(BaseModel):
    email: EmailStr
    name: str
    password: str


class ReadUser(BaseModel):
    email: EmailStr
    name: str

class UpdateUser(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str

    class Config:
        from_attributes = True

class UserDelete(BaseModel):
    email: EmailStr