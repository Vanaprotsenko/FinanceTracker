from fastapi import FastAPI
from src.dependencies import engine, Base
from src.router import user


app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(user.router)

