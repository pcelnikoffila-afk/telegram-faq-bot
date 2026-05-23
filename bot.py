import traceback
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

import asyncio

TOKEN = "8096940037:AAHHtT7eu7JnFw2YTKN3x-CbpXc9_54F9A4"

# ID группы
GROUP_CHAT_ID = -1003903288148

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Пользователи, ожидающие вопрос
waiting_for_question = set()

# Клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Задать вопрос факультету")],
        [KeyboardButton(text="Часто задаваемые вопросы")],
    ],
    resize_keyboard=True,
)


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

    await message.answer(
        welcome_text,
        reply_markup=main_keyboard,
    )


# Кнопка вопроса
@dp.message(F.text == "Задать вопрос факультету")
async def ask_question_handler(message: Message):

    waiting_for_question.add(message.from_user.id)

    await message.answer(
        "Напишите ваш вопрос"
    )


# FAQ
@dp.message(F.text == "Часто задаваемые вопросы")
async def faq_handler(message: Message):

    await message.answer(
        "Раздел FAQ скоро будет заполнен."
    )


# Пересылка сообщений
@dp.message()
async def forward_question_handler(message: Message):

    user_id = message.from_user.id

    if user_id in waiting_for_question:

        username = message.from_user.username

        if username:
            username_text = f"@{username}"
        else:
            username_text = "отсутствует"

        text = (
            f"📩 Новый вопрос от абитуриента\n\n"
            f"Имя: {message.from_user.full_name}\n"
            f"Username: {username_text}\n"
            f"ID: {message.from_user.id}\n\n"
            f"Вопрос:\n{message.text}"
        )

        try:

            await bot.send_message(
                GROUP_CHAT_ID,
                text,
            )

            print("Сообщение отправлено в группу")

            await message.answer(
                "Ваш вопрос отправлен сотрудникам факультета."
            )

        except Exception as e:

            print("ОШИБКА:")
            print(e)

            await message.answer(
                "Ошибка отправки сообщения."
            )

        waiting_for_question.remove(user_id)


async def main():
    print("BOT STARTING")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("CRASH:")
        traceback.print_exc()