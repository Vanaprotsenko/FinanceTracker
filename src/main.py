import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.router import user, record, mono, category


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(record.router)
app.include_router(mono.router)
app.include_router(category.router)


@app.get("/public/config")
async def get_public_config():
    bot_username = os.getenv("USERNAME_BOT", "home_statistics_bot").strip()
    bot_username = bot_username.lstrip("@")
    return {"telegram_bot_username": bot_username}


# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

