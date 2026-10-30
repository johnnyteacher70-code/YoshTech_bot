"""YoshTech Telegram Bot - Gemini AI integratsiyasi xizmati.

Ushbu modul Google Gemini AI API bilan asinxron (aiohttp orqali) ishlaydi,
foydalanuvchi savollariga javob qaytaradi va suhbat tarixini boshqaradi.
"""

import logging
from typing import Any
import aiohttp
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger("yoshtech_bot.ai")

# YoshTech AI uchun tizimli ko'rsatma (System Instruction)
SYSTEM_INSTRUCTION = (
    "Siz 'YoshTech' zamonaviy texnologiyalar va dasturlash o'quv markazining "
    "rasmiy, do'stona va aqlli sun'iy intellekt (AI) yordamchisisiz.\n\n"
    "Markazimiz haqida ma'lumotlar:\n"
    "• Yo'nalishlar:\n"
    "  1. Frontend dasturlash (HTML5, CSS3, JavaScript, React)\n"
    "  2. Python dasturlash (Python asoslari, OOP, Telegram botlar, ma'lumotlar bazasi)\n"
    "  3. Kompyuter savodxonligi (Windows, MS Office, internet va axborot xavfsizligi)\n"
    "  4. Grafik dizayn (Photoshop, Illustrator, Figma, brending)\n"
    "  5. Robototexnika (Arduino, elektronika, mikrokontrollerlar)\n"
    "• Manzil: Toshkent shahri, Yunusobod tumani\n"
    "• Kursga yozilish: Botdagi '📝 Kursga yozilish' tugmasi orqali amalga oshiriladi.\n\n"
    "Sizning vazifangiz:\n"
    "1. Dasturlash, IT yo'nalishlari, sun'iy intellekt, texnologiyalar va YoshTech kurslari "
    "bo'yicha barcha savollarga professional, to'g'ri va tushunarli javob berish.\n"
    "2. Foydalanuvchi qaysi tilda savol bersa (o'zbek, rus, ingliz va h.k.), shu tilda javob bering. Asosiy til — o'zbek tili.\n"
    "3. Javoblaringiz samimiy, chiroyli va qulay formatlangan bo'lsin. Murakkab atamalarni oddiy tilda tushuntiring."
)

# Ishonchli Gemini modellari ro'yxati (navbat bilan sinash uchun)
DEFAULT_MODELS = [
    "gemini-3.5-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-3.8-flash",
]


def split_text_for_telegram(text: str, max_chunk_size: int = 4000) -> list[str]:
    """Telegram xabar cheklovi (4096 belgi) uchun matnni qismlarga bo'ladi."""
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    lines = text.split("\n")
    current_chunk: list[str] = []
    current_length = 0

    for line in lines:
        if current_length + len(line) + 1 > max_chunk_size:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
            while len(line) > max_chunk_size:
                chunks.append(line[:max_chunk_size])
                line = line[max_chunk_size:]
        current_chunk.append(line)
        current_length += len(line) + 1

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


async def ask_gemini(
    prompt: str,
    history: list[dict[str, Any]] | None = None,
    model: str | None = None,
) -> str:
    """Google Gemini AI ga savol yuboradi va javob matnini qaytaradi."""
    api_key = GEMINI_API_KEY
    if not api_key:
        return (
            "⚠️ <b>Gemini AI API kaliti topilmadi!</b>\n\n"
            "Iltimos, bot ma'muri <code>.env</code> faylida <code>GEMINI_API_KEY</code> ni sozlashi kerak.\n"
            "API kalitni bepul olish manzili: https://aistudio.google.com/"
        )

    # Model nomzodlarini tuzish
    chosen_model = model or GEMINI_MODEL or "gemini-3.5-flash"
    models_to_try = [chosen_model]
    for fallback_model in DEFAULT_MODELS:
        if fallback_model not in models_to_try:
            models_to_try.append(fallback_model)

    # Xabarlar strukturasini tuzish
    contents: list[dict[str, Any]] = []
    if history:
        for msg in history:
            role = "model" if msg.get("role") in ("model", "assistant") else "user"
            text_content = msg.get("text", "")
            if text_content:
                contents.append({
                    "role": role,
                    "parts": [{"text": text_content}],
                })

    # Joriy savol
    contents.append({
        "role": "user",
        "parts": [{"text": prompt}],
    })

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}],
        },
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        },
    }

    timeout = aiohttp.ClientTimeout(total=25)

    last_error_msg = ""
    for current_model in models_to_try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{current_model}:generateContent?key={api_key}"
        )
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    status = response.status
                    data = await response.json()

                    if status == 200:
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                        return "Kechirasiz, sun'iy intellektdan bo'sh javob keldi. Iltimos, qaytadan urinib ko'ring."

                    error_info = data.get("error", {})
                    error_msg = error_info.get("message", "")
                    last_error_msg = error_msg
                    logger.warning("Gemini model '%s' xatosi [HTTP %s]: %s", current_model, status, error_msg)

                    # Agar kalit yaroqsiz bo'lsa (401, 403), keyingi modelni sinash foydasiz
                    if status in (401, 403):
                        return (
                            "❌ <b>Gemini API kaliti yaroqsiz yoki ruxsat yo'q!</b>\n\n"
                            "Iltimos, <code>.env</code> faylidagi <code>GEMINI_API_KEY</code> to'g'riligini tekshiring."
                        )

                    # Agar 404 (model topilmadi) yoki 503 (vaqtinchalik band) bo'lsa, keyingi modelga o'tadi
                    continue

        except (TimeoutError, aiohttp.ClientConnectorError) as e:
            logger.warning("Model '%s' ulanishida vaqtinchalik xatolik (%s). Keyingisiga o'tilmoqda...", current_model, e)
            continue
        except Exception as exc:
            logger.exception("Gemini API kutilmagan xatolik: %s", exc)
            last_error_msg = str(exc)
            continue

    if last_error_msg:
        return f"⚠️ Sun'iy intellekt bilan bog'lanishda vaqtinchalik xatolik yuz berdi: {last_error_msg}"
    return "⏳ AI serverlari ayni paytda band. Iltimos, bir necha daqiqadan so'ng qayta urinib ko'ring."
