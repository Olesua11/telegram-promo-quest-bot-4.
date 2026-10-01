# Telegram Promo Quest Bot

Демо Telegram-бота для рекламных спецпроектов.

## Что умеет

- главное меню на inline-кнопках;
- каталог контента по категориям;
- мини-квест из 3 шагов;
- персональный результат по ответам;
- форма сбора заявки;
- отправка заявки администратору;
- FSM-сценарии на aiogram 3.

## Стек

- Python 3.11+
- aiogram 3
- Telegram Bot API
- python-dotenv

## Запуск

1. Создай бота через `@BotFather` в Telegram.
2. Склонируй репозиторий.
3. Создай виртуальное окружение:

```bash
python -m venv .venv
```

4. Активируй его.

Windows:

```bash
.venv\\Scripts\\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

5. Установи зависимости:

```bash
pip install -r requirements.txt
```

6. Скопируй `.env.example` в `.env` и вставь токен:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_CHAT_ID=YOUR_TELEGRAM_ID
```

`ADMIN_CHAT_ID` можно оставить пустым — тогда бот будет работать без отправки заявок администратору.

7. Запусти:

```bash
python bot.py
```

## Для портфолио

Проект демонстрирует работу с Telegram Bot API, callback-кнопками, FSM, пользовательскими сценариями и базовой лид-формой.

> В реальном рекламном спецпроекте эту архитектуру можно расширить каталогом из базы данных, промокодами, CRM-интеграцией, аналитикой, webhook-деплоем и админ-панелью.
