"""YoshTech Telegram Bot - Asosiy menyu klaviaturasi.

Foydalanuvchiga asosiy bo'limlarga tezkor o'tish imkonini beruvchi doimiy ReplyKeyboardMarkup.
"""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu uchun ReplyKeyboardMarkup qaytaradi.
    
    Tugmalar:
    - 📚 Kurslar
    - 📝 Kursga yozilish
    - 🏫 Markaz haqida
    - 📞 Aloqa
    """
    keyboard = [
        [
            KeyboardButton(text="📚 Kurslar"),
            KeyboardButton(text="📝 Kursga yozilish"),
        ],
        [
            KeyboardButton(text="🏫 Markaz haqida"),
            KeyboardButton(text="📞 Aloqa"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )
