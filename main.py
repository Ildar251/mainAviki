import asyncio
import logging
import random
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "7528928353:AAH-vGfuanmuvGilzzDU3l54iS36JyzDMoY"
CHAT_ID = -1002469534667  # ID группы (int)
bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

plus_users = set()
accepting_pluses = False  # Флаг, разрешающий принимать плюсы

@dp.message(F.text == "/start")
async def start_command(message: Message):
    await message.answer("Бот запущен! Ожидаем плюсы по расписанию.")

async def send_plus_request():
    """Запрашивает плюсы и разрешает их сбор"""
    global accepting_pluses, plus_users
    plus_users.clear()
    accepting_pluses = True
    await bot.send_message(CHAT_ID, "Отправьте в чат 5 плюсов (+)")

def schedule_random_message():
    """Запланировать сбор плюсов на следующую среду в случайное время"""
    now = datetime.now()
    next_wednesday = now + timedelta(days=(3 - now.weekday()) % 7)  # Следующая среда
    random_hour = random.randint(9, 20)
    random_minute = random.randint(0, 59)
    scheduled_time = next_wednesday.replace(hour=random_hour, minute=random_minute, second=0)

    scheduler.add_job(send_plus_request, "date", run_date=scheduled_time)
    logging.info(f"Запланировано на {scheduled_time}")

@dp.message(F.text == "+")
async def count_pluses(message: Message):
    """Обрабатывает +, если разрешен их сбор"""
    global accepting_pluses

    if not accepting_pluses:
        return  # Игнорировать плюсы, если не идет их сбор

    if message.chat.id != CHAT_ID:
        return

    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    if user_id not in plus_users:
        plus_users.add((user_id, username))  # Сохраняем ID и имя пользователя
        remaining = 5 - len(plus_users)

        if remaining > 0:
            await bot.send_message(CHAT_ID, f"{username} готов! Осталось еще {remaining} хуесоса.")
        else:
            usernames = [user[1] for user in plus_users]  # Берем только имена
            await bot.send_message(CHAT_ID, f"Пять ебалнов готовы: {', '.join(usernames)}")
            plus_users.clear()
            accepting_pluses = False  # Отключаем сбор плюсов до следующего раза

async def main():
    logging.basicConfig(level=logging.INFO)
    scheduler.start()
    schedule_random_message()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
