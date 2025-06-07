from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv





load_dotenv(".env_template")

DATABASE_URL = "sqlite:///bizzytext.db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    return Session(engine)

# ✅ paste your retry commit function here:
def safe_commit(session, retries=5, delay=0.1):
    for i in range(retries):
        try:
            session.commit()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(delay)
            else:
                raise
    raise Exception("Database is locked after multiple retries")


