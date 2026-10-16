"""YoshTech Telegram Bot - Start va Asosiy Menyu handleri.

Ushbu modul /start, /help, /menu komandalarini va asosiy menyu ko'rinishini boshqaradi.
"""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.main_menu import get_main_menu_keyboard

start_router = Router(name="start_router")


@start_router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    """/start komandasi: Yangi foydalanuvchini samimiy kutib oladi va asosiy menyuni ko'rsatadi."""
    await state.clear()

    user_name = message.from_user.first_name if message.from_user else "Foydalanuvchi"

    welcome_text = (
        f"Assalomu alaykum, <b>{user_name}</b>!\n\n"
        "<b>YoshTech</b> o'quv markazining rasmiy demo botiga xush kelibsiz!\n"
        "Biz bilan zamonaviy texnologiyalar olamini o'rganing.\n\n"
        "Quyidagi tugmalar yordamida kurslarimiz bilan tanishishingiz, "
        "markaz haqida ma'lumot olishingiz yoki kursga yozilishingiz mumkin:"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """/help komandasi: Bot imkoniyatlari va foydalanish yo'riqnomasini tushuntiradi."""
    help_text = (
        "<b>YoshTech Demo Boti bo'yicha qo'llanma:</b>\n\n"
        "📌 <b>Asosiy buyruqlar:</b>\n"
        "• /start - Botni qayta ishga tushirish va asosiy menyu\n"
        "• /help - Bot imkoniyatlari haqida yordam\n"
        "• /menu - Asosiy menyuni ko'rsatish\n"
        "• /cancel - Ro'yxatdan o'tish jarayonini bekor qilish\n\n"
        "📌 <b>Asosiy bo'limlar:</b>\n"
        "• <b>📚 Kurslar:</b> Mavjud o'quv yo'nalishlari (Frontend, Python, Dizayn va h.k.)\n"
        "• <b>📝 Kursga yozilish:</b> O'zingiz qiziqqan kursga ariza topshirish (demo)\n"
        "• <b>🏫 Markaz haqida:</b> YoshTech o'quv markazi faoliyati haqida ma'lumot\n"
        "• <b>📞 Aloqa:</b> Biz bilan bog'lanish va manzil ma'lumotlari\n\n"
        "<i>Eslatma: Bu bot namoyish maqsadida yaratilgan demo loyihadir.</i>"
    )

    await message.answer(
        text=help_text,
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.message(Command("menu"))
async def handle_menu(message: Message, state: FSMContext) -> None:
    """/menu komandasi: Asosiy menyu klaviaturasini qayta chaqiradi."""
    await state.clear()
    await message.answer(
        text="Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu_keyboard(),
    )
