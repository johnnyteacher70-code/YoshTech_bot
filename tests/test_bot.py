"""YoshTech Telegram Bot - Testlar to'plami.

Ushbu testlar ma'lumotlar validatsiyasi, konfiguratsiya tekshiruvi
va routerlarning to'g'ri ulanishini tekshiradi.
"""

import sys
from pathlib import Path
import pytest

# Loyiha ildiz papkasini sys.path ga qo'shish
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import validate_config
from handlers import (
    about_router,
    contact_router,
    courses_router,
    fallback_router,
    registration_router,
    start_router,
)
from utils.validators import validate_and_normalize_phone, validate_full_name


class TestNameValidation:
    """Ism va familiya validatsiyasi testlari."""

    def test_valid_names(self):
        valid_cases = [
            ("Ali Valiyev", "Ali Valiyev"),
            ("g'anisher o'ktamov", "G'anisher O'ktamov"),
            ("Sanjarbek Jo'rayev", "Sanjarbek Jo'rayev"),
            ("Aziza Karimova", "Aziza Karimova"),
            ("Abdulloh Mirzo", "Abdulloh Mirzo"),
            ("John Doe", "John Doe"),
            ("   Zarina   Nematova   ", "Zarina Nematova"),
        ]
        for raw_name, expected in valid_cases:
            is_valid, result = validate_full_name(raw_name)
            assert is_valid is True, f"Failed for {raw_name}: {result}"
            assert result == expected

    def test_invalid_names(self):
        invalid_cases = [
            "",
            "   ",
            None,
            "Ali",               # Faqat 1 ta so'z
            "Ab",                # Juda qisqa
            "123 456",           # Raqamlar
            "Ali! Valiyev",      # Taqiqlangan belgi (!)
            "Valiyev @ Ali",     # Taqiqlangan belgi (@)
            "A" * 75 + " Bbb",   # Juda uzun (> 70 belgi)
        ]
        for raw_name in invalid_cases:
            is_valid, error = validate_full_name(raw_name)
            assert is_valid is False, f"Should be invalid for: {raw_name}"
            assert isinstance(error, str) and len(error) > 0


class TestPhoneValidation:
    """Telefon raqami validatsiyasi va normalizatsiyasi testlari."""

    def test_valid_phone_numbers(self):
        valid_cases = [
            ("+998901234567", "+998901234567"),
            ("998901234567", "+998901234567"),
            ("901234567", "+998901234567"),
            ("+998 (90) 123-45-67", "+998901234567"),
            ("90 123 45 67", "+998901234567"),
            ("+998 97 765 43 21", "+998977654321"),
            ("881112233", "+998881112233"),
            ("33 999 88 77", "+998339998877"),
            ("77 555 44 33", "+998775554433"),
        ]
        for raw_phone, expected in valid_cases:
            is_valid, result = validate_and_normalize_phone(raw_phone)
            assert is_valid is True, f"Failed for {raw_phone}: {result}"
            assert result == expected

    def test_invalid_phone_numbers(self):
        invalid_cases = [
            "",
            "   ",
            None,
            "salom",
            "12345",                    # Juda qisqa
            "+12345678901",             # AQSH raqami (998 emas)
            "+998111234567",            # Noto'g'ri operator kodi (11)
            "+998001234567",            # Noto'g'ri operator kodi (00)
            "+99890123456789",          # Juda uzun raqam
        ]
        for raw_phone in invalid_cases:
            is_valid, error = validate_and_normalize_phone(raw_phone)
            assert is_valid is False, f"Should be invalid for: {raw_phone}"
            assert isinstance(error, str) and len(error) > 0


class TestConfigAndArchitecture:
    """Konfiguratsiya va arxitektura tekshiruvlari."""

    def test_missing_token_raises_error(self, monkeypatch):
        """Token bo'sh yoki placeholder bo'lganda ValueError chiqarishi kerak."""
        monkeypatch.setattr("config.BOT_TOKEN", "")
        with pytest.raises(ValueError) as excinfo:
            validate_config()
        assert "XATOLIK: Telegram Bot Tokeni topilmadi" in str(excinfo.value)

        monkeypatch.setattr("config.BOT_TOKEN", "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE")
        with pytest.raises(ValueError):
            validate_config()

    def test_valid_token_passes(self, monkeypatch):
        """To'g'ri token muvaffaqiyatli qabul qilinishi kerak."""
        dummy_token = "1234567890:ABCdefGhIJKlmNoPQRstuVWXyz"
        monkeypatch.setattr("config.BOT_TOKEN", dummy_token)
        assert validate_config() == dummy_token

    def test_dispatcher_and_routers_integrity(self):
        """Barcha routerlar dispatcherga xatosiz ulanishi va circular import bo'lmasligi kerak."""
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(start_router)
        dp.include_router(courses_router)
        dp.include_router(registration_router)
        dp.include_router(about_router)
        dp.include_router(contact_router)
        dp.include_router(fallback_router)

        # 6 ta router muvaffaqiyatli ulandi
        assert len(dp.sub_routers) == 6
