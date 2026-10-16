"""YoshTech Telegram Bot - Noma'lum xabarlar uchun fallback handleri.

Ushbu modul foydalanuvchi menyudan tashqari yoki kutilmagan xabar yozganda
muloyimlik bilan yordam beradi va asosiy menyuni taqdim etadi.
"""

from aiogram import Router
from aiogram.types import Message
from keyboards.main_menu import get_main_menu_keyboard

fallback_router = Router(name="fallback_router")


@fallback_router.message()
async def handle_unknown_message(message: Message) -> None:
    """Hech qaysi handlerga mos kelmagan xabarlarga javob qaytaradi."""
    text = (
        "Kechirasiz, men ushbu xabarni tushunmadim. 🤔\n\n"
        "Iltimos, quyidagi menyu tugmalaridan birini tanlang yoki "
        "batafsil ma'lumot olish uchun /help buyrug'ini yuboring."
    )
    await message.answer(
        text=text,
        reply_markup=get_main_menu_keyboard(),
    )
