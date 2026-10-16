"""YoshTech Telegram Bot - Kurslar bo'limi handleri.

Ushbu modul markazning 5 ta asosiy o'quv yo'nalishi haqida batafsil ma'lumot beradi:
1. Frontend dasturlash
2. Python dasturlash
3. Kompyuter savodxonligi
4. Grafik dizayn
5. Robototexnika
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from keyboards.course_menu import (
    COURSES_DATA,
    get_course_details_keyboard,
    get_courses_inline_keyboard,
    get_phone_request_keyboard,
)
from keyboards.main_menu import get_main_menu_keyboard
from states.registration import RegistrationStates

courses_router = Router(name="courses_router")

# Kurslar bo'yicha batafsil ma'lumotlar lug'ati (demo tarkib)
COURSE_DETAILS = {
    "frontend": {
        "title": "Frontend dasturlash",
        "description": "Zamonaviy veb-saytlar va interaktiv veb-ilovalarning ko'rinadigan qismini yaratish bo'yicha amaliy kurs.",
        "suitable_for": "Dasturlashga yangi qiziqqanlar, ijodkorlik va texnologiyani uyg'unlashtirishni istagan boshlovchilar.",
        "benefits": (
            "• HTML5 va CSS3 (Flexbox, Grid) asoslari\n"
            "• Zamonaviy JavaScript (ES6+) imkoniyatlari\n"
            "• React freymvorki bilan ishlash ko'nikmalari\n"
            "• Portfolio uchun amaliy loyihalar yaratish"
        ),
    },
    "python": {
        "title": "Python dasturlash",
        "description": "Dunyoning eng mashhur dasturlash tillaridan biri orqali dasturlash mantig'i, algoritmlar va amaliy loyihalarni o'rganish kursi.",
        "suitable_for": "Mantiqiy fikrlashga qiziquvchilar, backend dasturchi yoki ma'lumotlar tahlilchisi bo'lishni rejalashtirganlar.",
        "benefits": (
            "• Python sintaksisi va chuqur OOP tushunchalari\n"
            "• Telegram botlar yaratish (aiogram yordamida)\n"
            "• Ma'lumotlar bazasi va fayllar bilan ishlash\n"
            "• Toza va xatosiz kod yozish madaniyati"
        ),
    },
    "computer_literacy": {
        "title": "Kompyuter savodxonligi",
        "description": "Kompyuterdan professional va erkin foydalanish, ofis dasturlari hamda raqamli xavfsizlik asoslari.",
        "suitable_for": "Kompyuter bilan endi tanishayotganlar, ofis xodimlari va o'quvchilar.",
        "benefits": (
            "• Windows operatsion tizimi bilan samarali ishlash\n"
            "• Microsoft Office (Word, Excel, PowerPoint) ko'nikmalari\n"
            "• Internetda qidiruv va bulutli xizmatlardan (Google Drive) foydalanish\n"
            "• Kiberxavfsizlik va axborotni himoyalash asoslari"
        ),
    },
    "graphic_design": {
        "title": "Grafik dizayn",
        "description": "Zamonaviy vizual kontent, logotiplar, ijtimoiy tarmoq postlari va brending dizaynlarini yaratish bo'yicha ijodiy kurs.",
        "suitable_for": "Vizual san'at va ijodkorlikka qiziquvchilar, SMM va marketing sohasida dizayn qilmoqchi bo'lganlar.",
        "benefits": (
            "• Adobe Photoshop dasturida rasmlarga ishlov berish\n"
            "• Adobe Illustrator dasturida vektorli grafika yaratish\n"
            "• Figma orqali zamonaviy interfeys eskizlarini chizish\n"
            "• Ranglar nazariyasi, kompozitsiya va tipografika qoidalari"
        ),
    },
    "robotics": {
        "title": "Robototexnika",
        "description": "Elektronika asoslari, mikrokontrollerlar va robotlarni o'z qo'llari bilan yasash hamda dasturlash kursi.",
        "suitable_for": "Maktab o'quvchilari, texnika va ixtirochilikka qiziqqan yoshlar.",
        "benefits": (
            "• Arduino platformasi va mikrokontrollerlar bilan ishlash\n"
            "• Sensorlar, motorlar va sxemalar bilan amaliy tajriba\n"
            "• C/C++ tillari asosida robotlarni dasturlash\n"
            "• Mantiqiy va muhandislik fikrlash qobiliyatini rivojlantirish"
        ),
    },
}


@courses_router.message(F.text == "📚 Kurslar")
async def show_courses_list(message: Message) -> None:
    """Foydalanuvchi asosiy menyudan '📚 Kurslar' tugmasini bosganda ishga tushadi."""
    text = (
        "<b>YoshTech o'quv yo'nalishlari:</b>\n\n"
        "Quyidagi kurslardan birini tanlab, uning tavsifi, kimlarga mosligi "
        "va beradigan foydalari haqida to'liq ma'lumot olishingiz mumkin:"
    )
    await message.answer(
        text=text,
        reply_markup=get_courses_inline_keyboard(),
    )


@courses_router.callback_query(F.data == "back_to_courses")
async def callback_back_to_courses(callback: CallbackQuery) -> None:
    """Kurslar ro'yxatiga qaytish inline tugmasi."""
    text = (
        "<b>YoshTech o'quv yo'nalishlari:</b>\n\n"
        "Quyidagi kurslardan birini tanlab, uning tavsifi va afzalliklari bilan tanishing:"
    )
    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_courses_inline_keyboard(),
        )
    await callback.answer()


@courses_router.callback_query(F.data.startswith("view_course:"))
async def callback_view_course_details(callback: CallbackQuery) -> None:
    """Tanlangan kurs haqida batafsil ma'lumotni ko'rsatish."""
    course_id = callback.data.split("view_course:")[1]
    course = COURSE_DETAILS.get(course_id)

    if not course:
        await callback.answer("Kechirasiz, bunday kurs topilmadi.", show_alert=True)
        return

    text = (
        f"🎯 <b>Kurs nomi:</b> {course['title']}\n\n"
        f"📖 <b>Qisqacha tavsif:</b>\n{course['description']}\n\n"
        f"👥 <b>Kimlar uchun mo'ljallangan:</b>\n{course['suitable_for']}\n\n"
        f"✨ <b>Kursda nimalarni o'rganasiz:</b>\n{course['benefits']}\n\n"
        "<i>Eslatma: Bu namoyish (demo) xarakteridagi ma'lumotdir. "
        "Dars jadvali va guruhlar bo'yicha batafsil ma'lumot olish uchun ro'yxatdan o'tishingiz mumkin.</i>"
    )

    if callback.message:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_course_details_keyboard(course_id),
        )
    await callback.answer()


@courses_router.callback_query(F.data == "back_to_main_menu")
async def callback_back_to_main_menu(callback: CallbackQuery) -> None:
    """Inline menyudan asosiy menyuga qaytish."""
    if callback.message:
        await callback.message.delete()
        await callback.message.answer(
            text="Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer()


@courses_router.callback_query(F.data.startswith("enroll_course:"))
async def callback_enroll_course(callback: CallbackQuery, state: FSMContext) -> None:
    """Kurs sahifasidan to'g'ridan-to'g'ri ro'yxatdan o'tishni boshlash (kurs tanlangan holda)."""
    course_id = callback.data.split("enroll_course:")[1]
    course_title = COURSES_DATA.get(course_id)

    if not course_title:
        await callback.answer("Kurs topilmadi.", show_alert=True)
        return

    # FSM holatini tozalash va tanlangan kursni saqlab qo'yish
    await state.clear()
    await state.update_data(selected_course=course_title)

    # Birinchi qadam: Ism-familiyani so'rash
    await state.set_state(RegistrationStates.full_name)

    if callback.message:
        await callback.message.answer(
            text=(
                f"Siz <b>'{course_title}'</b> kursini tanladingiz.\n\n"
                "Ro'yxatdan o'tish uchun, iltimos, <b>ism va familiyangizni</b> kiriting\n"
                "(Masalan: <i>Ali Valiyev</i>):"
            ),
            reply_markup=get_main_menu_keyboard(),
        )

    await callback.answer()
