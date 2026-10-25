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


async def create_table_db():
    try:
        conn = await connection_db()
        await conn.execute("""
            Create table if not exists users (
                users_id serial primary key,
                username varchar(200),
                full_name varchar(200),
                telegram_id varchar(200),
                is_admin boolean default false,
                is_active boolean default true,
                created_at timestamp default now()
            );

            Create table if not exists classes (
                classes_id serial primary key,
                telegram_id varchar(200),
                title varchar(200),
                capacity int check (capacity > 0),
                class_date timestamp default now(),
                is_active boolean default true,
                created_at timestamp default now()
            );

            Create table if not exists bookings (
                bookings_id serial primary key,
                telegram_id varchar(200),
                class_id int references classes(classes_id),
                booked_at timestamp default now(),
                is_active boolean default true,
                created_at timestamp default now()
            );

        """)

        print("Table created!")

    except Exception as Error:
        print(f"Create table error: {Error}")

    finally:
        await conn.close()