"""YoshTech Telegram Bot - Kursga yozilish (FSM) handleri.

Foydalanuvchidan qadamma-qadam ma'lumotlarni to'plash:
1. Ism-familiya
2. Telefon raqam (kontakt ulashish yoki qo'lda yozish orqali)
3. O'quv kursini tanlash (agar avval tanlanmagan bo'lsa)
4. Ma'lumotlarni tasdiqlash yoki bekor qilish
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from keyboards.course_menu import (
    COURSES_DATA,
    get_confirmation_keyboard,
    get_course_selection_keyboard,
    get_phone_request_keyboard,
)
from keyboards.main_menu import get_main_menu_keyboard
from states.registration import RegistrationStates
from utils.validators import validate_and_normalize_phone, validate_full_name

registration_router = Router(name="registration_router")


# ==========================================================
# 0. Ro'yxatdan o'tishni bekor qilish (Har qanday holatda)
# ==========================================================
@registration_router.message(Command("cancel"))
@registration_router.message(F.text == "❌ Bekor qilish")
async def cancel_registration_handler(message: Message, state: FSMContext) -> None:
    """Foydalanuvchi istalgan bosqichda jarayonni bekor qilishi mumkin."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            text="Hozirda faol ro'yxatdan o'tish jarayoni mavjud emas.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await state.clear()
    await message.answer(
        text="Ro'yxatdan o'tish jarayoni bekor qilindi. Bosh menyudasiz.",
        reply_markup=get_main_menu_keyboard(),
    )


@registration_router.callback_query(F.data == "cancel_registration")
async def callback_cancel_registration(callback: CallbackQuery, state: FSMContext) -> None:
    """Inline tugma orqali bekor qilish."""
    await state.clear()
    if callback.message:
        await callback.message.edit_text("❌ Ro'yxatdan o'tish bekor qilindi.")
        await callback.message.answer(
            text="Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer()


# ==========================================================
# 1. Asosiy menyudan ro'yxatdan o'tishni boshlash
# ==========================================================
@registration_router.message(F.text == "📝 Kursga yozilish")
async def start_registration_from_menu(message: Message, state: FSMContext) -> None:
    """Asosiy menyudagi '📝 Kursga yozilish' tugmasi orqali jarayonni boshlash."""
    await state.clear()
    await state.set_state(RegistrationStates.full_name)

    await message.answer(
        text=(
            "YoshTech kurslariga ro'yxatdan o'tish jarayoni boshlandi.\n\n"
            "Iltimos, to'liq <b>ism va familiyangizni</b> kiriting:\n"
            "(Masalan: <i>Ali Valiyev</i>)\n\n"
            "<i>Jarayonni bekor qilish uchun /cancel buyrug'ini yuborishingiz mumkin.</i>"
        ),
        reply_markup=get_main_menu_keyboard(),
    )


# ==========================================================
# 2. Ism-familiyani qabul qilish va tekshirish
# ==========================================================
@registration_router.message(RegistrationStates.full_name, F.text)
async def process_full_name(message: Message, state: FSMContext) -> None:
    """Foydalanuvchi kiritgan ism-familiyani qabul qilish va tekshirish."""
    is_valid, result = validate_full_name(message.text)

    if not is_valid:
        await message.answer(
            text=f"⚠️ {result}\n\nIltimos, ism va familiyangizni qaytadan kiriting:",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    # To'g'ri ismni saqlaymiz
    await state.update_data(full_name=result)

    # Telefon raqami bosqichiga o'tamiz
    await state.set_state(RegistrationStates.phone_number)

    await message.answer(
        text=(
            f"Rahmat, <b>{result}</b>!\n\n"
            "Endi bog'lanish uchun <b>telefon raqamingizni</b> yuboring.\n"
            "Quyidagi <b>'📱 Telefon raqamni yuborish'</b> tugmasini bosishingiz yoki "
            "raqamni qo'lda kiritishingiz mumkin (Masalan: <i>+998901234567</i>):"
        ),
        reply_markup=get_phone_request_keyboard(),
    )


@registration_router.message(RegistrationStates.full_name)
async def process_full_name_invalid_content(message: Message) -> None:
    """Foydalanuvchi matn o'rniga stiker, rasm yoki boshqa media yuborsa."""
    await message.answer(
        text="Iltimos, ism va familiyangizni matn ko'rinishida yozing (Masalan: <i>Ali Valiyev</i>):"
    )


# ==========================================================
# 3. Telefon raqamini qabul qilish (Kontakt yoki matn)
# ==========================================================
@registration_router.message(RegistrationStates.phone_number, F.contact)
async def process_phone_contact(message: Message, state: FSMContext) -> None:
    """Telegramning kontakt ulashish tugmasi orqali yuborilgan raqamni qabul qilish."""
    if not message.contact or not message.contact.phone_number:
        await message.answer("Telefon raqami aniqlanmadi. Iltimos, raqamni qo'lda kiriting:")
        return

    raw_phone = message.contact.phone_number
    is_valid, normalized_phone = validate_and_normalize_phone(raw_phone)

    if not is_valid:
        await message.answer(
            text=f"⚠️ {normalized_phone}\n\nIltimos, amaldagi O'zbekiston telefon raqamini kiriting:",
            reply_markup=get_phone_request_keyboard(),
        )
        return

    await state.update_data(phone_number=normalized_phone)
    await proceed_after_phone(message, state)


@registration_router.message(RegistrationStates.phone_number, F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    """Foydalanuvchi qo'lda yozgan telefon raqamini qabul qilish va tekshirish."""
    is_valid, result = validate_and_normalize_phone(message.text)

    if not is_valid:
        await message.answer(
            text=f"⚠️ {result}\n\nIltimos, to'g'ri telefon raqamini kiriting:",
            reply_markup=get_phone_request_keyboard(),
        )
        return

    await state.update_data(phone_number=result)
    await proceed_after_phone(message, state)


@registration_router.message(RegistrationStates.phone_number)
async def process_phone_invalid_content(message: Message) -> None:
    """Telefon o'rniga noto'g'ri media kelsa."""
    await message.answer(
        text="Iltimos, telefon raqamingizni '📱 Telefon raqamni yuborish' tugmasi orqali "
             "yoki matn ko'rinishida yuboring (Masalan: +998901234567):",
        reply_markup=get_phone_request_keyboard(),
    )


async def proceed_after_phone(message: Message, state: FSMContext) -> None:
    """Telefon kiritilgandan keyingi qadamni aniqlaydi.
    
    Agar kurs allaqachon tanlangan bo'lsa (kurs sahifasidan kelingan bo'lsa),
    to'g'ridan-to'g'ri tasdiqlash bosqichiga o'tadi. Aks holda kurs tanlash so'raladi.
    """
    user_data = await state.get_data()
    selected_course = user_data.get("selected_course")

    if selected_course:
        # Kurs oldindan tanlangan bo'lsa, to'g'ridan-to'g'ri tasdiqlashga o'tamiz
        await state.set_state(RegistrationStates.confirmation)
        await show_confirmation_summary(message, state)
    else:
        # Kurs tanlanmagan bo'lsa, kurslar ro'yxatini chiqaramiz
        await state.set_state(RegistrationStates.course)
        await message.answer(
            text="Ajoyib! Endi o'zingiz o'rganmoqchi bo'lgan <b>kursni tanlang</b>:",
            reply_markup=get_course_selection_keyboard(),
        )


# ==========================================================
# 4. Kursni tanlash
# ==========================================================
@registration_router.callback_query(RegistrationStates.course, F.data.startswith("select_course:"))
async def process_course_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Foydalanuvchi inline menyudan kursni tanlaganda."""
    course_id = callback.data.split("select_course:")[1]
    course_title = COURSES_DATA.get(course_id)

    if not course_title:
        await callback.answer("Bunday kurs mavjud emas.", show_alert=True)
        return

    await state.update_data(selected_course=course_title)
    await state.set_state(RegistrationStates.confirmation)

    if callback.message:
        await callback.message.delete()
        await show_confirmation_summary(callback.message, state)

    await callback.answer()


@registration_router.message(RegistrationStates.course)
async def process_course_invalid_message(message: Message) -> None:
    """Foydalanuvchi kursni inline tugmalar orqali tanlashi kerakligini eslatish."""
    await message.answer(
        text="Iltimos, quyidagi tugmalardan birini bosib kursni tanlang:",
        reply_markup=get_course_selection_keyboard(),
    )


# ==========================================================
# 5. Ariza xulosasini ko'rsatish va tasdiqlash
# ==========================================================
async def show_confirmation_summary(message: Message, state: FSMContext) -> None:
    """Kiritilgan ma'lumotlar xulosasini ko'rsatadi va tasdiqlashni so'raydi."""
    data = await state.get_data()
    full_name = data.get("full_name", "Noma'lum")
    phone = data.get("phone_number", "Noma'lum")
    course = data.get("selected_course", "Noma'lum")

    summary_text = (
        "📋 <b>Ariza ma'lumotlarini tekshiring:</b>\n\n"
        f"👤 <b>Talaba:</b> {full_name}\n"
        f"📞 <b>Telefon:</b> {phone}\n"
        f"🎯 <b>Tanlangan kurs:</b> {course}\n\n"
        "Ma'lumotlar to'g'ri bo'lsa, <b>'✅ Tasdiqlash'</b> tugmasini bosing:"
    )

    await message.answer(
        text=summary_text,
        reply_markup=get_confirmation_keyboard(),
    )


@registration_router.callback_query(RegistrationStates.confirmation, F.data == "confirm_registration")
async def process_final_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """Arizani yakuniy tasdiqlash (demo rejimida)."""
    # FSM ma'lumotlarini tozalaymiz
    await state.clear()

    success_text = (
        "🎉 <b>Arizangiz demo rejimida qabul qilindi!</b>\n\n"
        "Rahmat! Bu namuna bot bo'lgani uchun ma'lumotlaringiz bazaga saqlanmaydi "
        "va hech kim siz bilan bog'lanmaydi.\n\n"
        "YoshTech bilan zamonaviy kasblarni o'rganishda sizga omad tilaymiz!"
    )

    if callback.message:
        await callback.message.edit_text(text=success_text)
        await callback.message.answer(
            text="Siz yana asosiy menyudasiz:",
            reply_markup=get_main_menu_keyboard(),
        )

    await callback.answer("Arizangiz qabul qilindi (demo)!")
