"""YoshTech Telegram Bot - Kurslar va ro'yxatdan o'tish klaviaturalari.

Ushbu modulda kurslarni ko'rish, tanlash, tasdiqlash va bekor qilish uchun
qayta ishlatiluvchi Inline va Reply klaviaturalar jamlangan.
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# Kurslar ro'yxati va ularning kalitlari (ID)
COURSES_DATA = {
    "frontend": "Frontend dasturlash",
    "python": "Python dasturlash",
    "computer_literacy": "Kompyuter savodxonligi",
    "graphic_design": "Grafik dizayn",
    "robotics": "Robototexnika",
}


def get_courses_inline_keyboard() -> InlineKeyboardMarkup:
    """Kurslar ro'yxatini ko'rsatish uchun inline klaviatura."""
    inline_keyboard = []
    for course_id, course_title in COURSES_DATA.items():
        inline_keyboard.append([
            InlineKeyboardButton(
                text=f"💻 {course_title}",
                callback_data=f"view_course:{course_id}",
            )
        ])

    inline_keyboard.append([
        InlineKeyboardButton(
            text="🔙 Asosiy menyu",
            callback_data="back_to_main_menu",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_course_details_keyboard(course_id: str) -> InlineKeyboardMarkup:
    """Alohida kurs tafsilotlari ko'rsatilgandagi tugmalar.
    
    - Kursga to'g'ridan-to'g'ri yozilish
    - Kurslar ro'yxatiga qaytish
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="📝 Shu kursga yozilish",
                callback_data=f"enroll_course:{course_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Barcha kurslar",
                callback_data="back_to_courses",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_course_selection_keyboard() -> InlineKeyboardMarkup:
    """Ro'yxatdan o'tish jarayonida kursni tanlash uchun inline klaviatura."""
    inline_keyboard = []
    for course_id, course_title in COURSES_DATA.items():
        inline_keyboard.append([
            InlineKeyboardButton(
                text=course_title,
                callback_data=f"select_course:{course_id}",
            )
        ])
    inline_keyboard.append([
        InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data="cancel_registration",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamini ulashish uchun Reply klaviatura.
    
    Foydalanuvchi tugmani bosib kontaktini yuborishi yoki qo'lda raqam kiritishi mumkin.
    """
    keyboard = [
        [
            KeyboardButton(
                text="📱 Telefon raqamni yuborish",
                request_contact=True,
            )
        ],
        [
            KeyboardButton(text="❌ Bekor qilish"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    """FSM bosqichlarida bekor qilish imkoniyatini beruvchi oddiy klaviatura."""
    keyboard = [
        [
            KeyboardButton(text="❌ Bekor qilish"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Ro'yxatdan o'tish arizasini yakuniy tasdiqlash uchun inline klaviatura."""
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data="confirm_registration",
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="cancel_registration",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
