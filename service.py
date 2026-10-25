from connection import *


async def create_user(username, full_name, telegram_id):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into users(username, full_name, telegram_id) values
        ($1, $2, $3)
        """, username, full_name, str(telegram_id))
    except Exception as Error:
        print(f"Create user Error: {Error}")
    finally:
        await conn.close()


async def get_user_by_id(telegram_id):
    try:
        conn = await connection_db()
        user = await conn.fetchrow("""
        select * from users where telegram_id = $1
        """, str(telegram_id))
        return user
    except Exception as Error:
        print(f"Get user by id Error: {Error}")
    finally:
        await conn.close()


async def add_class(title, capacity):
    try:
        conn = await connection_db()
        class_id = await conn.fetchrow("""
        insert into classes(title, capacity)
        values ($1, $2)
        returning classes_id
        """, title, capacity)
        return class_id
    except Exception as Error:
        print(f"Add class Error: {Error}")
    finally:
        await conn.close()


async def get_all_classes():
    try:
        conn = await connection_db()
        classes = await conn.fetch("""
        select classes.*, classes.capacity - count(bookings.bookings_id) as free_places from classes
        left join bookings on classes.classes_id = bookings.class_id and bookings.is_active = true
        where classes.is_active = true
        group by classes.classes_id
        order by classes.class_date
        """)
        return classes
    except Exception as Error:
        print(f"Get classes Error: {Error}")
    finally:
        await conn.close()


async def book_class(telegram_id, class_id):
    try:
        conn = await connection_db()

        class_info = await conn.fetchrow("""
        select * from classes
        where classes_id = $1 and is_active = true
        """, class_id)

        if not class_info:
            return "not found"

        booking = await conn.fetchrow("""
        select * from bookings
        where telegram_id = $1 and class_id = $2 and is_active = true
        """, str(telegram_id), class_id)

        if booking:
            return "already_booked"

        count = await conn.fetchval("""
        select count(*) from bookings
        where class_id = $1 and is_active = true
        """, class_id)

        if count >= class_info["capacity"]:
            return "full"

        await conn.execute("""
        insert into bookings(telegram_id, class_id) values
        ($1, $2)
        """, str(telegram_id), class_id)

        return "success"

    except Exception as Error:
        print(f"Book class Error: {Error}")
        return "error"
    finally:
        await conn.close()