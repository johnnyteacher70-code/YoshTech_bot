"""YoshTech Telegram Bot - Gemini AI suhbat va Rasm generatsiyasi handleri.

Ushbu modul foydalanuvchilarga Google Gemini AI bilan bevosita muloqot qilish,
savol berish, maslahat olish hamda AI orqali yuqori sifatli rasmlar chizish
imkonini yaratadi.
"""

import logging
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from keyboards.ai_menu import get_ai_chat_keyboard
from keyboards.main_menu import get_main_menu_keyboard
from states.ai import AIStates
from utils.ai_service import ask_gemini, split_text_for_telegram
from utils.image_service import generate_ai_image, is_image_request

logger = logging.getLogger("yoshtech_bot.handlers.ai")

ai_router = Router(name="ai_router")

# Asosiy menyu tugmalari ro'yxati (AI suhbatidan chiqish uchun tekshirishga)
MAIN_MENU_BUTTONS = {
    "📚 Kurslar",
    "📝 Kursga yozilish",
    "🏫 Markaz haqida",
    "📞 Aloqa",
    "🤖 YoshTech AI",
}


async def _send_ai_chunks(message: Message, text: str) -> None:
    """Telegram xabar cheklovini hisobga olgan holda javobni yuboradi."""
    chunks = split_text_for_telegram(text)
    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await message.answer(chunk, parse_mode=None)


async def _process_image_generation(message: Message, prompt: str) -> None:
    """Rasm generatsiyasini amalga oshiruvchi va rasm qilib yuboruvchi yordamchi funksiya."""
    if message.bot:
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        except Exception:
            pass

    wait_msg = await message.answer("🎨 <i>Rasm chizilmoqda, iltimos bir oz kuting (10-15 soniya)...</i>")

    image_bytes = await generate_ai_image(prompt)
    if image_bytes:
        photo = BufferedInputFile(image_bytes, filename="yoshtech_ai.jpg")
        caption = f"🎨 <b>AI chizgan rasm:</b>\n<i>«{prompt[:200]}»</i>"
        try:
            await message.answer_photo(photo=photo, caption=caption)
            try:
                await wait_msg.delete()
            except Exception:
                pass
            return
        except Exception as exc:
            logger.error("Rasm yuborishda xatolik: %s", exc)

    await wait_msg.edit_text(
        "⚠️ Kechirasiz, rasmni chizishda vaqtinchalik xatolik yuz berdi. "
        "Iltimos, tavsifni boshqacharoq qilib qayta urinib ko'ring."
    )


@ai_router.message(Command("rasm"))
@ai_router.message(Command("image"))
async def handle_image_command(message: Message) -> None:
    """/rasm yoki /image buyrug'i orqali rasm generatsiya qilish."""
    text_parts = (message.text or "").split(maxsplit=1)
    if len(text_parts) > 1 and text_parts[1].strip():
        prompt = text_parts[1].strip()
        await _process_image_generation(message, prompt)
    else:
        await message.answer(
            "🎨 <b>Rasm chizish uchun tavsif kiriting:</b>\n\n"
            "Masalan:\n"
            "<code>/rasm Kosmosda suzayotgan astronavt mushuk</code>\n"
            "<code>/rasm Toshkent 2050 yilda kiberpank uslubida</code>\n"
            "<code>/rasm Dasturlash o'rganayotgan aqlli robot bola</code>"
        )


@ai_router.message(Command("ai"))
async def handle_ai_command(message: Message, state: FSMContext) -> None:
    """/ai komandasi orqali savol berish yoki suhbat rejimini ochish."""
    text_parts = (message.text or "").split(maxsplit=1)

    if len(text_parts) > 1 and text_parts[1].strip():
        query = text_parts[1].strip()

        # Agar foydalanuvchi /ai ichida ham rasm so'ragan bo'lsa
        if is_image_request(query):
            await _process_image_generation(message, query)
            return

        if message.bot:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

        state_data = await state.get_data()
        history = state_data.get("ai_history", [])

        answer = await ask_gemini(prompt=query, history=history)

        history.append({"role": "user", "text": query})
        history.append({"role": "model", "text": answer})
        await state.update_data(ai_history=history[-10:])

        await _send_ai_chunks(message, answer)
        return

    await start_ai_chat_mode(message, state)


@ai_router.message(F.text == "🤖 YoshTech AI")
async def handle_ai_menu_button(message: Message, state: FSMContext) -> None:
    """'🤖 YoshTech AI' tugmasi bosilganda suhbat rejimiga kirish."""
    await start_ai_chat_mode(message, state)


async def start_ai_chat_mode(message: Message, state: FSMContext) -> None:
    """AI muloqot rejimini ishga tushirish."""
    await state.set_state(AIStates.chatting)
    current_data = await state.get_data()
    if "ai_history" not in current_data:
        await state.update_data(ai_history=[])

    welcome_text = (
        "🤖 <b>YoshTech AI Yordamchisiga xush kelibsiz!</b>\n\n"
        "Men sizga matnli savollaringizga javob berish bilan birga, <b>rasmlar ham chizib bera olaman</b>! 🎨\n\n"
        "💡 <b>Imkoniyatlarim:</b>\n"
        "• Dasturlash va IT kurslari haqida ma'lumot berish\n"
        "• Kodlar tahlili va savollarga javob qaytarish\n"
        "• <b>AI Rasmlar chizish:</b> Shunchaki <i>«... rasmini chiz»</i> deb yozing!\n\n"
        "💬 <i>Savolingizni yoki rasm tavsifini yozib yuboring:</i>"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_ai_chat_keyboard(),
    )


@ai_router.message(AIStates.chatting, F.text == "🎨 Rasm yaratish")
async def handle_ai_image_prompt_helper(message: Message) -> None:
    """'🎨 Rasm yaratish' tugmasi bosilganda yo'riqnoma berish."""
    await message.answer(
        "🎨 <b>Qanday rasm chizishni xohlaysiz?</b>\n\n"
        "Quyidagicha yozib yuboring:\n"
        "• <i>Kosmosda kofe ichayotgan yoqimli robot bola</i>\n"
        "• <i>Toshkent teleminorasi kelajakda neon chiroqlarda</i>\n"
        "• <i>Dasturchi xonasi, monitorlar va kiberpank dizayn</i>\n\n"
        "Qani, xohlagan fantaziyangizni yozib yuboring:",
        reply_markup=get_ai_chat_keyboard(),
    )


@ai_router.message(AIStates.chatting, F.text == "❌ Suhbatni yakunlash")
@ai_router.message(AIStates.chatting, Command("cancel"))
async def handle_ai_exit(message: Message, state: FSMContext) -> None:
    """AI suhbat rejimini yakunlash va asosiy menyuga qaytish."""
    await state.clear()
    await message.answer(
        text="AI bilan suhbat yakunlandi. Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu_keyboard(),
    )


@ai_router.message(AIStates.chatting, F.text == "🗑 Tarixni tozalash")
async def handle_ai_clear_history(message: Message, state: FSMContext) -> None:
    """AI suhbat xotirasini tozalash."""
    await state.update_data(ai_history=[])
    await message.answer(
        text="🧹 <b>Suhbat xotirasi tozalandi!</b>\n\nEndi yangi savolingizni berishingiz mumkin:",
        reply_markup=get_ai_chat_keyboard(),
    )


@ai_router.message(AIStates.chatting)
async def handle_ai_message(message: Message, state: FSMContext) -> None:
    """AI suhbat rejimida kelgan har qanday savol yoki rasm so'roviga javob berish."""
    text = (message.text or "").strip()

    if text in MAIN_MENU_BUTTONS and text != "🤖 YoshTech AI":
        await state.clear()
        await message.answer(
            text="Siz asosiy menyuga qaytdingiz.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    if not text:
        await message.answer(
            "Iltimos, menga matn ko'rinishida savol yuboring.",
            reply_markup=get_ai_chat_keyboard(),
        )
        return

    # Foydalanuvchi rasm chizishni so'rayotganini tekshirish
    if is_image_request(text):
        await _process_image_generation(message, text)
        return

    # Matnli savolga typing statusi
    if message.bot:
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        except Exception:
            pass

    state_data = await state.get_data()
    history = state_data.get("ai_history", [])

    answer = await ask_gemini(prompt=text, history=history)

    history.append({"role": "user", "text": text})
    history.append({"role": "model", "text": answer})
    await state.update_data(ai_history=history[-10:])

    await _send_ai_chunks(message, answer)
