import asyncio
import logging
import os
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it to .env")

logging.basicConfig(level=logging.INFO)


@dataclass(frozen=True)
class Category:
    title: str
    text: str


CATEGORIES = {
    "recipes": Category(
        title="🍪 Новогодние рецепты",
        text=(
            "<b>3 идеи для праздничного стола:</b>\n\n"
            "1. Имбирное печенье\n"
            "2. Сырные шарики\n"
            "3. Безалкогольный пунш\n\n"
            "Такой раздел легко расширить до полноценного каталога."
        ),
    ),
    "promo": Category(
        title="🎁 Акции",
        text=(
            "<b>Промо-механика:</b> пользователь выбирает категорию, "
            "проходит мини-квест и получает персональный результат или промокод."
        ),
    ),
    "about": Category(
        title="ℹ️ О проекте",
        text=(
            "Демо рекламного Telegram-бота для спецпроектов: меню, callback-кнопки, "
            "FSM-сценарии, мини-квест и сбор заявки."
        ),
    ),
}


class LeadForm(StatesGroup):
    name = State()
    contact = State()


class Quest(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()


QUEST_ANSWERS = {}


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🍪 Рецепты", callback_data="category:recipes"),
                InlineKeyboardButton(text="🎁 Акции", callback_data="category:promo"),
            ],
            [InlineKeyboardButton(text="🎮 Пройти мини-квест", callback_data="quest:start")],
            [InlineKeyboardButton(text="📩 Оставить заявку", callback_data="lead:start")],
            [InlineKeyboardButton(text="ℹ️ О проекте", callback_data="category:about")],
        ]
    )


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")]]
    )


def quest_keyboard(question: int) -> InlineKeyboardMarkup:
    options = {
        1: [("🎨 Яркий", "bright"), ("🖤 Минимализм", "minimal")],
        2: [("🎁 Призы", "prizes"), ("🏆 Рейтинг", "rating")],
        3: [("⚡ Быстро", "fast"), ("🧩 Подольше", "deep")],
    }
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"quest:{question}:{value}")]
            for label, value in options[question]
        ]
    )


async def send_admin_lead(bot: Bot, user: Message, name: str, contact: str) -> None:
    if not ADMIN_CHAT_ID:
        return
    text = (
        "<b>Новая заявка из демо-бота</b>\n"
        f"Имя: {name}\n"
        f"Контакт: {contact}\n"
        f"Telegram: @{user.from_user.username or 'нет username'}\n"
        f"ID: <code>{user.from_user.id}</code>"
    )
    try:
        await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=text)
    except Exception:
        logging.exception("Could not send lead to admin")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    @dp.message(CommandStart())
    async def start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(
            "👋 <b>Привет!</b>\n\n"
            "Это демо промо-бота для рекламных спецпроектов. "
            "Здесь есть каталог, мини-квест и сбор заявки.",
            reply_markup=main_menu(),
        )

    @dp.message(Command("menu"))
    async def menu_command(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu())

    @dp.callback_query(F.data == "menu")
    async def menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.message.edit_text("Главное меню:", reply_markup=main_menu())
        await callback.answer()

    @dp.callback_query(F.data.startswith("category:"))
    async def category_handler(callback: CallbackQuery) -> None:
        key = callback.data.split(":", 1)[1]
        category = CATEGORIES[key]
        await callback.message.edit_text(
            f"<b>{category.title}</b>\n\n{category.text}",
            reply_markup=back_menu(),
        )
        await callback.answer()

    @dp.callback_query(F.data == "quest:start")
    async def quest_start(callback: CallbackQuery, state: FSMContext) -> None:
        QUEST_ANSWERS[callback.from_user.id] = []
        await state.set_state(Quest.q1)
        await callback.message.edit_text(
            "🎮 <b>Мини-квест</b>\n\n"
            "Вопрос 1/3. Какой стиль рекламного проекта тебе ближе?",
            reply_markup=quest_keyboard(1),
        )
        await callback.answer()

    @dp.callback_query(Quest.q1, F.data.startswith("quest:1:"))
    async def quest_q1(callback: CallbackQuery, state: FSMContext) -> None:
        QUEST_ANSWERS.setdefault(callback.from_user.id, []).append(callback.data.split(":")[-1])
        await state.set_state(Quest.q2)
        await callback.message.edit_text(
            "Вопрос 2/3. Что интереснее в механике?",
            reply_markup=quest_keyboard(2),
        )
        await callback.answer()

    @dp.callback_query(Quest.q2, F.data.startswith("quest:2:"))
    async def quest_q2(callback: CallbackQuery, state: FSMContext) -> None:
        QUEST_ANSWERS.setdefault(callback.from_user.id, []).append(callback.data.split(":")[-1])
        await state.set_state(Quest.q3)
        await callback.message.edit_text(
            "Вопрос 3/3. Какой формат прохождения выбрать?",
            reply_markup=quest_keyboard(3),
        )
        await callback.answer()

    @dp.callback_query(Quest.q3, F.data.startswith("quest:3:"))
    async def quest_q3(callback: CallbackQuery, state: FSMContext) -> None:
        answers = QUEST_ANSWERS.setdefault(callback.from_user.id, [])
        answers.append(callback.data.split(":")[-1])
        await state.clear()

        if "bright" in answers and "prizes" in answers:
            result = "Тебе подходит <b>яркий промо-квест с призовой механикой</b>."
        elif "minimal" in answers and "rating" in answers:
            result = "Тебе подходит <b>минималистичный челлендж с рейтингом участников</b>."
        else:
            result = "Тебе подходит <b>интерактивный бот с коротким игровым сценарием</b>."

        await callback.message.edit_text(
            f"✅ <b>Готово!</b>\n\n{result}\n\n"
            "В коммерческом проекте здесь может быть промокод, персональный результат, "
            "лид-форма или переход на лендинг.",
            reply_markup=back_menu(),
        )
        await callback.answer("Результат готов")

    @dp.callback_query(F.data == "lead:start")
    async def lead_start(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(LeadForm.name)
        await callback.message.edit_text(
            "📩 <b>Оставить заявку</b>\n\nКак тебя зовут?\n\n"
            "Для отмены отправь /cancel"
        )
        await callback.answer()

    @dp.message(Command("cancel"))
    async def cancel(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("Заявка отменена.", reply_markup=main_menu())

    @dp.message(LeadForm.name)
    async def lead_name(message: Message, state: FSMContext) -> None:
        if not message.text or len(message.text.strip()) < 2:
            await message.answer("Напиши имя текстом, пожалуйста.")
            return
        await state.update_data(name=message.text.strip())
        await state.set_state(LeadForm.contact)
        await message.answer("Оставь телефон, email или Telegram для связи:")

    @dp.message(LeadForm.contact)
    async def lead_contact(message: Message, state: FSMContext) -> None:
        if not message.text or len(message.text.strip()) < 3:
            await message.answer("Укажи контакт текстом, пожалуйста.")
            return
        data = await state.get_data()
        name = data.get("name", "Не указано")
        contact = message.text.strip()
        await send_admin_lead(bot, message, name, contact)
        await state.clear()
        await message.answer(
            "✅ Спасибо! Заявка сохранена в рамках демо-сценария.",
            reply_markup=main_menu(),
        )

    @dp.message()
    async def fallback(message: Message) -> None:
        await message.answer(
            "Я пока понимаю команды и кнопки меню. Нажми /start или /menu.",
            reply_markup=main_menu(),
        )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
