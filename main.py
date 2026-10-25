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

async def main():
    await create_table_db()
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
