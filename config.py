"""YoshTech Telegram Bot - Konfiguratsiya moduli.

Ushbu modul muhit o'zgaruvchilarini (.env) yuklaydi va BOT_TOKEN mavjudligini tekshiradi.
Token mavjud bo'lmasa yoki namuna ko'rinishida qolib ketgan bo'lsa,
dastur tushunarli xatolik xabari bilan to'xtatiladi.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env faylini loyiha ildiz papkasidan yuklash
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

# Placeholder yoki bo'sh token tekshiruvi
PLACEHOLDER_TOKENS = {
    "",
    "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE",
    "YOUR_TELEGRAM_BOT_TOKEN_HERE",
    "BOT_TOKEN_HERE",
}

# Administratorlarning Telegram ID raqamlarini yuklash
def _load_admin_ids() -> list[int]:
    raw_admins = os.getenv("ADMIN_IDS", "").strip()
    if not raw_admins:
        return []
    ids = []
    for part in raw_admins.split(","):
        clean_part = part.strip()
        if clean_part.isdigit():
            ids.append(int(clean_part))
    return ids


ADMIN_IDS: list[int] = _load_admin_ids()

# Veb boshqaruv paneli uchun administrator paroli
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "yoshtech2026").strip()


def is_admin(user_id: int | None) -> bool:
    """Foydalanuvchi administrator ekanligini tekshiradi."""
    if not user_id:
        return False
    return user_id in ADMIN_IDS


def validate_config() -> str:
    """Bot tokenini tekshiradi va qaytaradi.
    
    Agar token kiritilmagan bo'lsa, foydalanuvchiga aniq yo'riqnoma bilan ValueError chiqaradi.
    """
    if not BOT_TOKEN or BOT_TOKEN in PLACEHOLDER_TOKENS:
        error_msg = (
            "\n" + "=" * 60 + "\n"
            "XATOLIK: Telegram Bot Tokeni topilmadi yoki noto'g'ri sozlangan!\n"
            "=" * 60 + "\n"
            "Botni ishga tushirish uchun quyidagi amallarni bajaring:\n"
            "1. Telegram orqali @BotFather ga kiring va yangi bot yarating (/newbot).\n"
            "2. BotFather bergan API tokenni nusxalang.\n"
            "3. Loyiha papkasidagi '.env' faylini oching va tokenni yozing:\n"
            "   BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRstuVWXyz\n"
            "4. Faylni saqlang va 'python bot.py' buyrug'ini qayta ishga tushiring.\n"
            "=" * 60
        )
        raise ValueError(error_msg)
    return BOT_TOKEN
