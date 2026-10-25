import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

pass_db = os.getenv("PASSWORD_DB")


async def connection_db():
    try:
        conn = await asyncpg.connect(
            user="postgres",
            database="gym_bot",
            password=pass_db,
            host="localhost",
            port=5432
        )
        return conn
    except Exception as Error:
        print(f"Connection error: {Error}")
        return None