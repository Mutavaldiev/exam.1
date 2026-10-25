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


async def cancel_booking(telegram_id, booking_id):
    conn = await connection_db()

    if conn is None:
        return "Database connection error."

    try:
        result = await conn.execute(
            """
            DELETE FROM bookings
            WHERE bookings_id = $1
            AND telegram_id = $2
            """,
            booking_id,
            telegram_id
        )

        if result == "DELETE 1":
            return "Booking cancelled successfully."

        return "Booking not found."

    except Exception as e:
        print(f"Cancel booking error: {e}")
        return "An error occurred while cancelling booking."

    finally:
        await conn.close()


async def get_my_bookings(telegram_id):
    conn = await connection_db()

    if conn is None:
        return []

    try:
        bookings = await conn.fetch(
            """
            SELECT c.classes_id, c.title, c.class_date FROM bookings b
            JOIN classes c ON b.class_id = c.classes_id
            WHERE b.telegram_id = $1 AND b.is_active = TRUE AND c.is_active = TRUE
            ORDER BY c.class_date
            """,
            str(telegram_id)
        )

        return bookings

    except Exception as Error:
        print(f"Get my bookings Error: {Error}")
        return []

    finally:
        await conn.close()