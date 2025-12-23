
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
import certifi
import config


USER = config.DB_USER
PASSWORD = config.DB_PASS
HOST = config.DB_HOST
PORT = config.DB_PORT
DB = config.DB_NAME

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
mongo_client = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def connect_to_mongo():
    global mongo_client
    mongo_client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
    return mongo_client


def get_mongo_db():
    return mongo_client.get_default_database()