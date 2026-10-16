"""YoshTech Telegram Bot - Noma'lum xabarlar uchun fallback handleri.

Ushbu modul foydalanuvchi menyudan tashqari yoki kutilmagan xabar yozganda
muloyimlik bilan yordam beradi va asosiy menyuni taqdim etadi.
"""

from aiogram import Router
from aiogram.types import Message
from config import ADMIN_IDS, is_admin
from keyboards.main_menu import get_main_menu_keyboard

fallback_router = Router(name="fallback_router")


@fallback_router.message()
async def handle_unknown_message(message: Message) -> None:
    """Hech qaysi handlerga mos kelmagan xabarlarga javob qaytaradi va adminga uzatadi."""
    # Agar xabar oddiy foydalanuvchidan kelgan bo'lsa, adminga yetkazamiz
    if message.from_user and not is_admin(message.from_user.id):
        user_info = f"<b>{message.from_user.full_name}</b>"
        if message.from_user.username:
            user_info += f" (@{message.from_user.username})"
        admin_alert = (
            f"💬 <b>FOYDALANUVCHIDAN XABAR:</b>\n\n"
            f"👤 <b>Kimdan:</b> {user_info}\n"
            f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
            f"📝 <b>Matn:</b> {message.text or '[Fayl/Media]'}"
        )
        if message.bot:
            for admin_id in ADMIN_IDS:
                try:
                    await message.bot.send_message(chat_id=admin_id, text=admin_alert)
                except Exception:
                    pass

    text = (
        "Xabaringiz qabul qilindi va administratorga yetkazildi! ✅\n\n"
        "Shuningdek, quyidagi menyu orqali kurslarimiz bilan tanishishingiz yoki "
        "yordam olish uchun /help buyrug'ini yuborishingiz mumkin."
    )
    await message.answer(
        text=text,
        reply_markup=get_main_menu_keyboard(),
    )
