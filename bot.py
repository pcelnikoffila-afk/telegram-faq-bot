import asyncio
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


TOKEN = "8096940037:AAHHtT7eu7JnFw2YTKN3x-CbpXc9_54F9A4"
GROUP_CHAT_ID = -1003903288148

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://telegram-faq-bot-q2b2.onrender.com/webhook"

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
    await message.answer(
        "Здравствуйте! 🤝🏻\n\nБот факультета работает через webhook.",
        reply_markup=main_keyboard,
    )


@dp.message(F.text == "Задать вопрос факультету")
async def ask_question_handler(message: Message):
    waiting_for_question.add(message.from_user.id)
    await message.answer("Напишите ваш вопрос")


@dp.message(F.text == "Часто задаваемые вопросы")
async def faq_handler(message: Message):
    await message.answer("FAQ скоро будет заполнен.")


@dp.message()
async def forward_question_handler(message: Message):

    user_id = message.from_user.id

    if user_id in waiting_for_question:

        username = message.from_user.username
        username_text = f"@{username}" if username else "отсутствует"

        text = (
            f"📩 Новый вопрос\n\n"
            f"Имя: {message.from_user.full_name}\n"
            f"Username: {username_text}\n"
            f"ID: {user_id}\n\n"
            f"Вопрос:\n{message.text}"
        )

        try:
            await bot.send_message(GROUP_CHAT_ID, text)
            await message.answer("Вопрос отправлен!")

        except Exception as e:
            print(e)
            await message.answer("Ошибка отправки.")

        waiting_for_question.remove(user_id)


# ---------------- WEBHOOK SERVER ----------------

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook set")


async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()



from aiogram.types import Update

async def handle(request):
    try:
        data = await request.json()

        print("UPDATE RECEIVED:", data)

        update = Update.model_validate(data)

        await dp.feed_update(bot, update)

        return web.Response(text="OK")

    except Exception as e:
        print("WEBHOOK ERROR:", repr(e))
        raise


app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)


# ---------------- RUN ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)