"""YoshTech Telegram Bot - AI Rasm generatsiyasi xizmati.

Ushbu modul foydalanuvchilarning matnli tavsiflari asosida yuqori sifatli
AI rasmlar chizadi va tayyorlaydi.
"""

import logging
import urllib.parse
import aiohttp
from utils.ai_service import ask_gemini

logger = logging.getLogger("yoshtech_bot.image")

IMAGE_TRIGGERS = (
    "rasm chiz",
    "rasmini chiz",
    "surat chiz",
    "suratini chiz",
    "rasm yarat",
    "rasm chiqar",
    "rasmini chiqar",
    "rasmini ber",
    "rasm ber",
    "chizib ber",
    "rasmini yarat",
    "draw",
    "generate image",
    "generate photo",
    "picture of",
    "image of",
)


def is_image_request(text: str) -> bool:
    """Foydalanuvchi matni rasm chizish haqida ekanligini aniqlaydi."""
    lower = text.lower().strip()
    return any(trigger in lower for trigger in IMAGE_TRIGGERS)


async def generate_ai_image(prompt: str) -> bytes | None:
    """Tavsif asosida sun'iy intellekt orqali rasm generatsiya qiladi va baytlarini qaytaradi."""
    try:
        # Promptni Gemini orqali tasvir generatori uchun boyitilgan inglizcha promptga aylantiramiz
        enhancement_prompt = (
            "You are an AI image prompt engineer. Convert the following request into a high quality, "
            "vivid English prompt for an image generator (like Flux/SDXL). "
            "Output ONLY the prompt text, no explanations, no quotes, maximum 35 words:\n"
            f"{prompt}"
        )
        en_prompt = await ask_gemini(enhancement_prompt)

        # Agar Gemini xato bersa, asl promptni ishlatamiz
        if not en_prompt or en_prompt.startswith("⚠️") or en_prompt.startswith("❌"):
            clean_prompt = prompt
        else:
            clean_prompt = en_prompt.strip().replace('"', '')

        logger.info("AI rasm uchun prompt: %s", clean_prompt)
        encoded_prompt = urllib.parse.quote(clean_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"

        timeout = aiohttp.ClientTimeout(total=35)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    image_bytes = await resp.read()
                    if len(image_bytes) > 2000:
                        return image_bytes
                logger.warning("Rasm generatoridan xatolik kodi keldi: HTTP %s", resp.status)
                return None
    except Exception as exc:
        logger.exception("Rasm yaratishda xatolik yuz berdi: %s", exc)
        return None
