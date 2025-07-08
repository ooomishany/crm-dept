from aiogram.fsm.state import State, StatesGroup

class ClientStates(StatesGroup):
    waiting_for_name = State()  # Ожидание ввода имени клиента
    waiting_for_username = State()  # Ожидание ввода ника в Telegram
    waiting_for_purchase_type = State()  # Ожидание выбора типа покупки
    waiting_for_payment_status = State()  # Ожидание выбора статуса оплаты
    waiting_for_currency = State()  # Ожидание выбора валюты
    waiting_for_payment_amount = State()  # Ожидание ввода суммы оплаты
    waiting_for_payment_date = State()  # Ожидание ввода даты оплаты
    waiting_for_purchase_duration = State()  # Новое состояние: выбор длительности покупки
    waiting_for_comment = State()  # Ожидание ввода комментария