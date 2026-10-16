"""YoshTech Telegram Bot - O'quv markazi haqida ma'lumot beruvchi handler.

Ushbu modul markaz faoliyati, maqsadlari va yo'nalishlari haqida ma'lumot beradi.
"""

from aiogram import F, Router
from aiogram.types import Message
from keyboards.main_menu import get_main_menu_keyboard

about_router = Router(name="about_router")


@about_router.message(F.text == "🏫 Markaz haqida")
async def handle_about(message: Message) -> None:
    """'🏫 Markaz haqida' tugmasi bosilganda ma'lumot beruvchi handler."""
    about_text = (
        "🏫 <b>YoshTech zamonaviy texnologiyalar o'quv markazi</b>\n\n"
        "<b>YoshTech</b> — yoshlar va barcha qiziquvchilarga zamonaviy axborot texnologiyalari, "
        "dasturlash va raqamli kasblarni o'rgatishga yo'naltirilgan zamonaviy o'quv markazidir.\n\n"
        "🚀 <b>Bizning asosiy yo'nalishlarimiz:</b>\n"
        "• Veb-dasturlash (Frontend)\n"
        "• Python dasturlash va botlar yaratish\n"
        "• Kompyuter savodxonligi va raqamli ko'nikmalar\n"
        "• Zamonaviy grafik dizayn\n"
        "• Yoshlar uchun robototexnika va elektronika\n\n"
        "💡 <b>Bizning maqsadimiz:</b>\n"
        "O'quvchilarga nafaqat nazariy bilimlarni berish, balki ularda amaliy ko'nikmalar, "
        "mantiqiy fikrlash va haqiqiy loyihalar ustida ishlash tajribasini shakllantirishdir.\n\n"
        "⚠️ <i>Eslatma: Ushbu bot YoshTech o'quv markazining namoyish (demo) loyihasi hisoblanadi.</i>"
    )

    await message.answer(
        text=about_text,
        reply_markup=get_main_menu_keyboard(),
    )
