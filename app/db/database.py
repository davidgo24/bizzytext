from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv(".env_template")

DATABASE_URL = "sqlite:///bizzytext.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)


