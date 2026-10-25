from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from service import *
from connection import *
import asyncio
import os

load_dotenv()

token = os.getenv("BOT_TOKEN")

bot = Bot(token=token)
dp = Dispatcher()


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 My Bookings")],
        [KeyboardButton(text="🏋️ Classes")],
        [KeyboardButton(text="🆘 Help")],
        [KeyboardButton(text="👤 Profile")],
    ],
    resize_keyboard=True,
)


@dp.message(CommandStart())
async def start_bot(message: Message):
    user = message.from_user

    if not await get_user_by_id(user.id):
        await create_user(user.username, user.full_name, user.id)

    await message.answer(f"""
👋 Hello, {user.full_name}!
🏋️ Welcome to Gym Booking!
📚 Use /help to see available commands.
""", reply_markup=main_kb)


@dp.message(F.text == "🆘 Help")
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(f"""
🏋️ Gym Booking — Help

🚀 /start — Start the bot
📚 /help — Show commands
👤 /show_profile — Show your profile
➕ /add_class — Add a class
📅 /classes — Show all classes
📝 /book — Book a class
❌ /cancel_booking — Cancel your booking
📋 /my_bookings — Show your bookings
""")



@dp.message(Command("show_profile"))
@dp.message(F.text == "👤 Profile")
async def show_profile(message: Message):
    user = await get_user_by_id(message.from_user.id)

    if not user:
        await message.answer("❌ User not found! Use /start first.")
        return

    await message.answer(f"""
👤 Your Profile

🆔 Telegram ID: {message.from_user.id}
📛 Full Name: {user['full_name']}
🔗 Username: @{user['username']}
📅 Joined: {user['created_at']}
""")


@dp.message(Command("add_class"))
async def add_class_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(f"""
➕ Add a Class
📌 Example: /add_class Yoga/10
📝 Format: /add_class Title/Capacity
""")
        return

    if not await check_admin(message.from_user.id):
        await message.answer("❌ Only admins can add classes!")
        return

    data = command.args.split("/")
    title = data[0]
    capacity = int(data[1])

    result = await add_class(title, capacity)

    if result:
        await message.answer(f"""
✅ Class added successfully!

🆔 Class ID: {result['classes_id']}
📚 Title: {title}
👥 Capacity: {capacity}
""")
    else:
        await message.answer("❌ Failed to add class.")


@dp.message(Command("classes"))
@dp.message(F.text == "🏋️ Classes")
async def classes_handler(message: Message):
    classes = await get_all_classes()

    if not classes:
        await message.answer("📭 No classes available.")
        return

    text = "🏋️ Available Classes:"

    for gym_class in classes:
        text += f"""
🆔 Class ID: {gym_class['classes_id']}
📚 Title: {gym_class['title']}
👥 Capacity: {gym_class['capacity']}
✅ Free Places: {gym_class['free_places']}
📅 Date: {gym_class['class_date']}

"""

    await message.answer(text)


@dp.message(Command("book"))
async def book_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(f"""
📝 Book a Class
📌 Example: /book 1
🔢 Enter the class ID after the command.
""")
        return

    data = command.args.split("/")
    class_id = int(data[0])

    result = await book_class(message.from_user.id, class_id)

    if result == "not found":
        await message.answer("❌ Class not found.")
    elif result == "full":
        await message.answer("😔 This class is full.")
    elif result == "already_booked":
        await message.answer("⚠️ You have already booked this class.")
    elif result == "success":
        await message.answer("✅ Your booking was successful!")
    else:
        await message.answer("❌ Booking failed.")


async def main():
    await create_table_db()
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
