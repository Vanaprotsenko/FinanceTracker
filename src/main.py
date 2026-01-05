from fastapi import FastAPI, Depends
from models.user import User
from schemas.user import UserBase, UserRead
from dependencies import engine, get_db, Base
from router import user


app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(user.router)

