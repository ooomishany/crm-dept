from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID
from notion_client import APIErrorCode, APIResponseError
from datetime import datetime

# Инициализация клиента Notion
notion = Client(auth=NOTION_TOKEN)


async def add_to_notion(data):
    """
    Добавляет данные о клиенте в таблицу "Клиенты".
    """
    new_page = {
        "Имя клиента": {
            "title": [
                {
                    "text": {
                        "content": data['Имя клиента']
                    }
                }
            ]
        },
        "Ник в телеграме": {
            "rich_text": [
                {
                    "text": {
                        "content": data['Ник в телеграме']
                    }
                }
            ]
        },
        "Тип покупки": {
            "select": {
                "name": data['Тип покупки']
            }
        },
        "Оплата": {
            "select": {
                "name": data['Оплата']
            }
        },
        "Комментарий": {
            "rich_text": [
                {
                    "text": {
                        "content": data['Комментарий']
                    }
                }
            ]
        }
    }

    # Добавляем поле "Сумма оплаты", только если оно указано
    if data.get('Сумма оплаты'):
        new_page["Сумма оплаты"] = {
            "rich_text": [
                {
                    "text": {
                        "content": data['Сумма оплаты']
                    }
                }
            ]
        }

    # Добавляем поле "Дата оплаты", только если оно указано
    if data.get('Дата оплаты'):
        new_page["Дата оплаты"] = {
            "date": {
                "start": data['Дата оплаты']  # Формат: ГГГГ-ММ-ДД
            }
        }

    # Добавляем поле "Длительность подписки", только если оно указано
    if data.get('Длительность покупки'):
        new_page["Длительность покупки"] = {
            "select": {
                "name": data['Длительность покупки']
            }
        }

    try:
        # Логируем данные перед отправкой
        print(f"Данные для отправки в Notion: {new_page}")

        # Отправляем данные в таблицу "Клиенты"
        print("Данные отправляются в таблицу 'Клиенты'.")
        notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=new_page)
        print("Данные успешно добавлены в таблицу 'Клиенты'.")

    except APIResponseError as e:
        if e.code == APIErrorCode.ObjectNotFound:
            print(f"Ошибка: База данных с ID {NOTION_DATABASE_ID} не найдена. Проверьте доступ интеграции.")
        else:
            print(f"Произошла ошибка при добавлении данных в Notion: {e}")
            print(f"Данные, которые вызвали ошибку: {new_page}")  # Логируем данные
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print(f"Данные, которые вызвали ошибку: {new_page}")  # Логируем данные