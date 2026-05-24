import asyncio
import traceback
import os
import threading

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from aiohttp import web


TOKEN = "8096940037:AAHHtT7eu7JnFw2YTKN3x-CbpXc9_54F9A4"  # лучше потом заменить на env
GROUP_CHAT_ID = -1003903288148

bot = Bot(token=TOKEN)
dp = Dispatcher()

waiting_for_question = set()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Задать вопрос факультету")],
        [KeyboardButton(text="Часто задаваемые вопросы")],
    ],
    resize_keyboard=True,
)


# ---------------- HANDLERS ----------------

@dp.message(CommandStart())
async def start_handler(message: Message):

    welcome_text = (
        "Здравствуйте, уважаемые абитуриенты! 🤝🏻\n\n"
        "Прием-бот Факультета мировой политики ГАУГН создан для того, "
        "чтобы вы могли задать любые интересующие вас вопросы о факультете "
        "напрямую сотрудникам учебной части.\n\n"
        "Внимание, администраторы бота — это действующие сотрудники факультета. "
        "Большая просьба соблюдать основные правила вежливости."
    )

    await message.answer(welcome_text, reply_markup=main_keyboard)


@dp.message(F.text == "Задать вопрос факультету")
async def ask_question_handler(message: Message):
    waiting_for_question.add(message.from_user.id)
    await message.answer("Напишите ваш вопрос")


@dp.message(F.text == "Часто задаваемые вопросы")
async def faq_handler(message: Message):
    await message.answer("Раздел FAQ скоро будет заполнен.")


@dp.message()
async def forward_question_handler(message: Message):

    user_id = message.from_user.id

    if user_id in waiting_for_question:

        username = message.from_user.username
        username_text = f"@{username}" if username else "отсутствует"

        text = (
            f"📩 Новый вопрос от абитуриента\n\n"
            f"Имя: {message.from_user.full_name}\n"
            f"Username: {username_text}\n"
            f"ID: {user_id}\n\n"
            f"Вопрос:\n{message.text}"
        )

        try:
            await bot.send_message(GROUP_CHAT_ID, text)

            await message.answer(
                "Ваш вопрос отправлен сотрудникам факультета."
            )

        except Exception as e:
            print("ОШИБКА:", e)
            await message.answer("Ошибка отправки сообщения.")

        waiting_for_question.remove(user_id)


# ---------------- WEB SERVER (для Render) ----------------

async def handle(request):
    return web.Response(text="Bot is running")


def run_web():
    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)


def start_web():
    thread = threading.Thread(target=run_web)
    thread.start()


# ---------------- MAIN ----------------

async def main():
    start_web()
    print("BOT STARTING")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        print("CRASH:")
        traceback.print_exc()