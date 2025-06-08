import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env_template")

DATABASE_URL = os.getenv("DATABASE_URL")

def run_migrations():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    files = sorted(os.listdir("app/db/migrations"))

    for file in files:
        with open(f"app/db/migrations/{file}", "r") as f:
            sql = f.read()
            print(f"Running migration: {file}")
            try:
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(f"Error in {file}: {e}")
                conn.rollback()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migrations()
