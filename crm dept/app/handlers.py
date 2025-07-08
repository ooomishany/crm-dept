from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import datetime
from app.states import ClientStates  # Импортируем ClientStates из states.py
from app.notion import add_to_notion
from aiogram.filters import Command

# Словарь для хранения данных о клиентах
clients = {}

# Обработчик команды /start
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Добавить клиента"))
    await message.answer("Выберите действие:", reply_markup=builder.as_markup(resize_keyboard=True))


# Обработчик кнопки "Добавить клиента"
async def add_client(message: types.Message, state: FSMContext):
    await state.update_data({
        'Имя клиента': '',
        'Ник в телеграме': '',
        'Тип покупки': '',
        'Оплата': '',
        'Дата оплаты': '',  # Поле для даты оплаты
        'Валюта': '',  # Поле для валюты
        'Сумма оплаты': '',  # Поле для суммы оплаты
        'Длительность покупки': '',  # Новое поле: длительность покупки
        'Комментарий': ''  # Поле для комментария
    })
    await message.answer("Введите имя клиента:")
    await state.set_state(ClientStates.waiting_for_name)  # Устанавливаем состояние waiting_for_name


# Обработчик ввода имени клиента
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data({'Имя клиента': message.text})
    await message.answer("Введите ник в Telegram:")
    await state.set_state(ClientStates.waiting_for_username)  # Устанавливаем состояние waiting_for_username


# Обработчик ввода ника в Telegram
async def process_username(message: types.Message, state: FSMContext):
    # Сохраняем ник в Telegram в состоянии
    await state.update_data({'Ник в телеграме': message.text})
    print(f"Ник в телеграме сохранен: {message.text}")  # Отладочный вывод

    # Создаем инлайн-кнопки для выбора типа покупки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Торговая группа", callback_data="trade_group"))
    builder.add(InlineKeyboardButton(text="Обучение", callback_data="training"))
    builder.add(InlineKeyboardButton(text="Обучение и Торговая группа", callback_data="both"))

    # Располагаем кнопки вертикально
    builder.adjust(1)

    await message.answer("Выберите тип покупки:", reply_markup=builder.as_markup())
    await state.set_state(ClientStates.waiting_for_purchase_type)


# Обработчик выбора типа покупки
async def process_purchase_type(callback: types.CallbackQuery, state: FSMContext):
    # Определяем тип покупки
    if callback.data == "trade_group":
        purchase_type = "Торговая группа"
    elif callback.data == "training":
        purchase_type = "Обучение"
    elif callback.data == "both":
        purchase_type = "Обучение и Торговая группа"
    else:
        await callback.answer("Неизвестный тип покупки.")
        return

    # Сохраняем тип покупки в состоянии
    await state.update_data({'Тип покупки': purchase_type})

    # Создаем инлайн-кнопки для выбора статуса оплаты
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Оплатил", callback_data="paid"))
    builder.add(InlineKeyboardButton(text="Не оплатил", callback_data="not_paid"))
    builder.add(InlineKeyboardButton(text="Не продлил", callback_data="not_renewed"))

    await callback.message.answer("Выберите статус оплаты:", reply_markup=builder.as_markup())
    await state.set_state(ClientStates.waiting_for_payment_status)
    await callback.answer()


# Обработчик выбора статуса оплаты
async def process_payment_status(callback: types.CallbackQuery, state: FSMContext):
    # Определяем статус оплаты
    if callback.data == "paid":
        payment_status = "Оплатил"
    elif callback.data == "not_paid":
        payment_status = "Не оплатил"
    elif callback.data == "not_renewed":
        payment_status = "Не продлил"
    else:
        await callback.answer("Неизвестный статус оплаты.")
        return

    # Сохраняем статус оплаты в состоянии
    await state.update_data({'Оплата': payment_status})

    # Если статус "Не оплатил" или "Не продлил", пропускаем шаги с валютой, суммой, датой и длительностью
    if payment_status in ["Не оплатил", "Не продлил"]:
        await state.update_data({
            'Валюта': None,
            'Сумма оплаты': None,
            'Дата оплаты': None,
            'Длительность покупки': None  # Пустое значение для длительности
        })
        await callback.message.answer("Введите комментарий:")
        await state.set_state(ClientStates.waiting_for_comment)
    else:
        # Если статус "Оплатил", переходим к выбору валюты
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="$", callback_data="currency_usd"))
        builder.add(InlineKeyboardButton(text="₽", callback_data="currency_rub"))

        await callback.message.answer("Выберите валюту оплаты:", reply_markup=builder.as_markup())
        await state.set_state(ClientStates.waiting_for_currency)

    await callback.answer()


# Обработчик выбора валюты
async def process_currency(callback: types.CallbackQuery, state: FSMContext):
    currency = "$" if callback.data == "currency_usd" else "₽"
    await state.update_data({'Валюта': currency})  # Сохраняем валюту в состояние

    await callback.message.answer("Введите сумму оплаты:")
    await state.set_state(ClientStates.waiting_for_payment_amount)  # Переходим к состоянию для ввода суммы
    await callback.answer()


# Обработчик ввода суммы оплаты
async def process_payment_amount(message: types.Message, state: FSMContext):
    try:
        payment_amount = float(message.text)  # Преобразуем ввод в число
        user_data = await state.get_data()
        currency = user_data.get('Валюта', '')  # Получаем валюту из состояния

        # Объединяем валюту и сумму в одну строку
        payment_info = f"{currency} {payment_amount}"

        await state.update_data({'Сумма оплаты': payment_info})  # Сохраняем в состояние
        await message.answer("Введите дату оплаты в формате ДД.ММ.ГГГГ:")
        await state.set_state(ClientStates.waiting_for_payment_date)  # Переходим к состоянию для ввода даты
    except ValueError:
        await message.answer("Неверный формат суммы. Введите число.")


# Обработчик ввода даты оплаты
async def process_payment_date(message: types.Message, state: FSMContext):
    user_input = message.text

    if user_input == "-":
        # Если пользователь ввел "-", сохраняем null или пропускаем поле
        await state.update_data({'Дата оплаты': None})
    else:
        try:
            # Преобразуем ввод пользователя в формат ISO 8601
            date_obj = datetime.strptime(user_input, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            await state.update_data({'Дата оплаты': formatted_date})
        except ValueError:
            await message.answer("Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ или '-' для пропуска.")
            return

    # Переходим к выбору длительности покупки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="1 месяц", callback_data="duration_1"))
    builder.add(InlineKeyboardButton(text="4 месяца", callback_data="duration_4"))
    builder.add(InlineKeyboardButton(text="Навсегда", callback_data="duration_forever"))

    await message.answer("Выберите длительность покупки:", reply_markup=builder.as_markup())
    await state.set_state(ClientStates.waiting_for_purchase_duration)


# Обработчик выбора длительности покупки
async def process_purchase_duration(callback: types.CallbackQuery, state: FSMContext):
    # Определяем длительность покупки
    if callback.data == "duration_1":
        duration = "1 месяц"
    elif callback.data == "duration_4":
        duration = "4 месяца"
    elif callback.data == "duration_forever":
        duration = "Навсегда"
    else:
        await callback.answer("Неизвестная длительность.")
        return

    # Сохраняем длительность в состоянии
    await state.update_data({'Длительность покупки': duration})

    # Переходим к вводу комментария
    await callback.message.answer("Введите комментарий:")
    await state.set_state(ClientStates.waiting_for_comment)
    await callback.answer()


# Обработчик ввода комментария
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data({'Комментарий': message.text})
    user_data = await state.get_data()

    try:
        # Сохраняем клиента в локальный словарь
        clients[user_data['Ник в телеграме']] = user_data

        # Добавляем данные в Notion
        await add_to_notion(user_data)

        # Отправляем сообщение об успешном добавлении
        await message.answer(
            f"Клиент {user_data['Имя клиента']} успешно добавлен!\n"
            f"Данные: {user_data}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении данных в Notion: {e}")

    # Очищаем состояние
    await state.clear()