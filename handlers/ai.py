"""YoshTech Telegram Bot - Gemini AI suhbat handleri.

Ushbu modul foydalanuvchilarga Google Gemini AI bilan bevosita muloqot qilish,
savol berish va maslahat olish imkonini yaratadi.
"""

import logging
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.ai_menu import get_ai_chat_keyboard
from keyboards.main_menu import get_main_menu_keyboard
from states.ai import AIStates
from utils.ai_service import ask_gemini, split_text_for_telegram

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
            # Avval chiroyli Markdown formatida yuborishga harakat qilamiz
            await message.answer(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # Agar Gemini qaytargan belgilar sababli Markdown xatosi bo'lsa, oddiy matn sifatida yuboramiz
            await message.answer(chunk, parse_mode=None)


@ai_router.message(Command("ai"))
async def handle_ai_command(message: Message, state: FSMContext) -> None:
    """/ai komandasi orqali savol berish yoki suhbat rejimini ochish."""
    # Buyruqdan keyingi matnni tekshiramiz: masalan "/ai Python nima?"
    text_parts = (message.text or "").split(maxsplit=1)

    if len(text_parts) > 1 and text_parts[1].strip():
        # Savol berilgan bo'lsa, bevosita javob beramiz
        query = text_parts[1].strip()
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

    # Savol berilmagan bo'lsa, suhbat rejimiga o'tkazamiz
    await start_ai_chat_mode(message, state)


@ai_router.message(F.text == "🤖 YoshTech AI")
async def handle_ai_menu_button(message: Message, state: FSMContext) -> None:
    """'🤖 YoshTech AI' tugmasi bosilganda suhbat rejimiga kirish."""
    await start_ai_chat_mode(message, state)


async def start_ai_chat_mode(message: Message, state: FSMContext) -> None:
    """AI muloqot rejimini ishga tushirish yordamchi funksiyasi."""
    await state.set_state(AIStates.chatting)
    # Yangi suhbat ochilganda tarixni bo'shatish yoki saqlash
    current_data = await state.get_data()
    if "ai_history" not in current_data:
        await state.update_data(ai_history=[])

    welcome_text = (
        "🤖 <b>YoshTech AI Yordamchisiga xush kelibsiz!</b>\n\n"
        "Men Google Gemini modeli asosida ishlayman va sizga quyidagi mavzularda yordam bera olaman:\n"
        "• Dasturlash tillari (Python, JavaScript, React, SQL va h.k.)\n"
        "• YoshTech o'quv markazimiz kurslari va yo'nalishlari\n"
        "• Kod tahlili, xatolarni tuzatish va foydali IT maslahatlar\n\n"
        "💬 <i>Savolingizni quyiga bemalol yozib yuboring:</i>\n\n"
        "<i>(Suhbatdan chiqish uchun quyidagi <b>❌ Suhbatni yakunlash</b> tugmasini bosing)</i>"
    )

    await message.answer(
        text=welcome_text,
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
    """AI suhbat rejimida kelgan har qanday matnli savolga javob berish."""
    text = (message.text or "").strip()

    # Agar foydalanuvchi asosiy menyu tugmasini bosgan bo'lsa, AI rejimidan chiqamiz
    if text in MAIN_MENU_BUTTONS and text != "🤖 YoshTech AI":
        await state.clear()
        # Fallback yoki boshqa routerlar ushlashi uchun javob beramiz
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

    # Typing statusini ko'rsatamiz
    if message.bot:
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        except Exception:
            pass

    state_data = await state.get_data()
    history = state_data.get("ai_history", [])

    answer = await ask_gemini(prompt=text, history=history)

    # Tarixga qo'shish (oxirgi 10 ta xabar)
    history.append({"role": "user", "text": text})
    history.append({"role": "model", "text": answer})
    await state.update_data(ai_history=history[-10:])

    await _send_ai_chunks(message, answer)
