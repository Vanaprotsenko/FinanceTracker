from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: str
    password: str

class ReadUser(BaseModel):
    email: EmailStr
    name: str

    class Config:
        orm_mode = True

class UpdateUser(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    init_data: str | None = None

    class Config:
        orm_mode = True

class UserDelete(BaseModel):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    init_data: str | None = None