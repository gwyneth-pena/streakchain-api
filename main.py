from fastapi import FastAPI
from contextlib import asynccontextmanager
from config import FRONTEND_URL
from db import connect_to_mongo, engine, Base, mongo_client
from sqlalchemy import text
from routes import habit_logs, habits, users
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
        print("Connected to database")

        connect_to_mongo()
        print("Connected to MongoDB")

    except Exception as e:
        print("Failed to connect to database", e)
    yield

    engine.dispose()
    
    if mongo_client:
        mongo_client.close()

    print("Disconnected from databases")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to StreakChain API - track your daily habit streaks with ease."}

app.include_router(users.router)
app.include_router(habits.router)
app.include_router(habit_logs.router)