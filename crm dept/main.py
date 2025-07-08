from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import types, F
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from config import API_TOKEN
from app.handlers import (
    cmd_start, add_client, process_name, process_username,
    process_purchase_type, process_payment_status,
    clients, process_payment_amount, process_comment, process_currency, process_payment_date, process_purchase_duration
)
from app.states import ClientStates  # Импортируем ClientStates из states.py

# Включаем логирование
# logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация хэндлеров
dp.message.register(cmd_start, Command("start"))
dp.message.register(add_client, F.text == "Добавить клиента")
dp.message.register(process_name, ClientStates.waiting_for_name)
dp.message.register(process_username, ClientStates.waiting_for_username)
dp.callback_query.register(process_purchase_type, ClientStates.waiting_for_purchase_type)
dp.callback_query.register(process_payment_status, ClientStates.waiting_for_payment_status)
dp.callback_query.register(process_currency, ClientStates.waiting_for_currency)  # Новый хэндлер
dp.message.register(process_payment_amount, ClientStates.waiting_for_payment_amount)
dp.message.register(process_payment_date, ClientStates.waiting_for_payment_date)  # Новый хэндлер
dp.message.register(process_comment, ClientStates.waiting_for_comment)
dp.callback_query.register(process_purchase_duration, ClientStates.waiting_for_purchase_duration)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())



