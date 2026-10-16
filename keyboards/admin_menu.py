"""YoshTech Telegram Bot - Administrator paneli klaviaturalari.

Ushbu modulda administrator menyusi va amallar uchun mo'ljallangan Inline klaviaturalar joylashgan.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Administratorning asosiy boshqaruv paneli tugmalari."""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"),
            InlineKeyboardButton(text="📋 Oxirgi arizalar", callback_data="admin:recent"),
        ],
        [
            InlineKeyboardButton(text="📥 Arizalarni yuklab olish (CSV)", callback_data="admin:export"),
        ],
        [
            InlineKeyboardButton(text="📢 Xabar tarqatish (Broadcast)", callback_data="admin:broadcast"),
        ],
        [
            InlineKeyboardButton(text="❌ Yopish", callback_data="admin:close"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_application_action_keyboard(app_id: int) -> InlineKeyboardMarkup:
    """Yangi tushgan arizani boshqarish tugmalari."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Bog'lanildi deb belgilash",
                callback_data=f"admin:status:{app_id}:boglanildi",
            ),
        ],
        [
            InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"admin:status:{app_id}:bekor",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Xabar tarqatishni bekor qilish tugmasi."""
    keyboard = [
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:cancel_broadcast"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
