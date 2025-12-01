from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import engine
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected to database")
    except Exception as e:
        print("Failed to connect to database", e)
    yield
    engine.dispose()
    print("Disconnected from database")


app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Welcome to SteakFlow API - track your daily habit streaks with ease."}