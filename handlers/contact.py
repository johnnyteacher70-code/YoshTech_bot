"""YoshTech Telegram Bot - Aloqa ma'lumotlari handleri.

Ushbu modul markaz bilan bog'lanish ma'lumotlarini namuna ko'rinishida taqdim etadi.
Barcha ma'lumotlar ochiq va tahrirlash uchun qulay qilib joylashtirilgan.
"""

from aiogram import F, Router
from aiogram.types import Message
from keyboards.main_menu import get_main_menu_keyboard

contact_router = Router(name="contact_router")

# Aloqa uchun demo ma'lumotlar (o'zgartirish uchun qulay)
CONTACT_INFO = {
    "phone": "+998 (71) 000-00-00 (Demo)",
    "telegram": "@yoshtech_demo_admin",
    "channel": "@yoshtech_demo_channel",
    "address": "Toshkent shahri, Yunusobod tumani, Demo ko'chasi, 1-uy",
    "working_hours": "Dushanba - Shanba: 09:00 - 18:00 (Yakshanba dam olish)",
}


@contact_router.message(F.text == "📞 Aloqa")
async def handle_contact(message: Message) -> None:
    """'📞 Aloqa' tugmasi bosilganda bog'lanish ma'lumotlarini ko'rsatish."""
    contact_text = (
        "📞 <b>YoshTech markazi bilan bog'lanish:</b>\n\n"
        f"📱 <b>Telefon raqam:</b> {CONTACT_INFO['phone']}\n"
        f"✈️ <b>Telegram admin:</b> {CONTACT_INFO['telegram']}\n"
        f"📢 <b>Rasmiy kanal:</b> {CONTACT_INFO['channel']}\n"
        f"📍 <b>Manzil:</b> {CONTACT_INFO['address']}\n"
        f"🕒 <b>Ish vaqti:</b> {CONTACT_INFO['working_hours']}\n\n"
        "<i>Eslatma: Yuqoridagi kontaktlar namuna (demo) sifatida ko'rsatilgan. "
        "Loyiha sozlamalari orqali haqiqiy ma'lumotlarga osongina o'zgartirilishi mumkin.</i>"
    )

    await message.answer(
        text=contact_text,
        reply_markup=get_main_menu_keyboard(),
    )
