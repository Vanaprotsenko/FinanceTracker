from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: str
    password: str

class ReadUser(BaseModel):
    email: EmailStr
    name: str
    telegram_username: str | None = None
    telegram_id: str | None = None

    class Config:
        orm_mode = True

class UpdateUser(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

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


class UserSaveMonoToken(BaseModel):
    mono_token: str


class UserResponseMonoToken(BaseModel):
    response: str

class VerifyTelegramRequest(BaseModel):
    telegram_id: str