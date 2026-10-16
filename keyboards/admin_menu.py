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


def get_application_action_keyboard(app_id: int, user_id: int | None = None) -> InlineKeyboardMarkup:
    """Yangi tushgan arizani boshqarish va talabaga xabar yozish tugmalari."""
    rows = []
    if user_id:
        rows.append([
            InlineKeyboardButton(
                text="💬 Talabaga xabar yozish",
                callback_data=f"admin:reply:{user_id}",
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="✅ Bog'lanildi",
            callback_data=f"admin:status:{app_id}:boglanildi",
        ),
        InlineKeyboardButton(
            text="❌ Rad etish",
            callback_data=f"admin:status:{app_id}:bekor",
        ),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_user_message_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Foydalanuvchidan xabar kelganda javob qaytarish tugmasi."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="✍️ Javob yozish",
                callback_data=f"admin:reply:{user_id}",
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_reply_to_user_keyboard() -> InlineKeyboardMarkup:
    """Talabaga xabar yozishni bekor qilish tugmasi."""
    keyboard = [
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:cancel_reply"),
        ]
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
