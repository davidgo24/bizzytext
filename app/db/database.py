# app/db/database.py
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker


# Load environment variables from .env file
load_dotenv(".env_template")

# Pull DB URL from env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in environment")

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()