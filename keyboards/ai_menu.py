"""YoshTech Telegram Bot - Gemini AI suhbati klaviaturalari."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_ai_chat_keyboard() -> ReplyKeyboardMarkup:
    """AI bilan muloqot paytidagi Reply klaviatura."""
    keyboard = [
        [
            KeyboardButton(text="🎨 Rasm yaratish"),
            KeyboardButton(text="🗑 Tarixni tozalash"),
        ],
        [
            KeyboardButton(text="❌ Suhbatni yakunlash"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )
