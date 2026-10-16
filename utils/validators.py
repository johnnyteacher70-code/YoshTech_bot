"""YoshTech Telegram Bot - Ma'lumotlarni tekshirish (validatsiya) moduli.

Ushbu modulda foydalanuvchi kiritgan ism-familiya va telefon raqamini
tekshirish hamda standart ko'rinishga keltirish (normalizatsiya) funksiyalari joylashgan.
"""

import re
from typing import Tuple


def validate_full_name(name: str | None) -> Tuple[bool, str]:
    """Foydalanuvchi ism va familiyasini tekshiradi.
    
    Talablar:
    - Bo'sh bo'lmasligi kerak.
    - Kamida 2 ta so'zdan (ism va familiya) iborat bo'lishi kerak.
    - Uzunligi 4 tadan 70 tagacha belgidan iborat bo'lishi kerak.
    - Faqat harflar, bo'sh joy, defis va o'zbek tilidagi tutuq belgilariga (', `, ’) ruxsat beriladi.
    
    Returns:
        Tuple[bool, str]: (to'g'ri_yoki_noto'g'ri, tozalangan_ism_yoki_xatolik_xabari)
    """
    if not name or not isinstance(name, str):
        return False, "Ism-familiya kiritilmadi. Iltimos, ismingiz va familiyangizni yozing."

    # Ortiqcha bo'shliqlarni tozalash
    cleaned = " ".join(name.strip().split())

    if len(cleaned) < 4:
        return False, "Ism-familiya juda qisqa. Kamida 4 ta belgidan iborat bo'lishi kerak."

    if len(cleaned) > 70:
        return False, "Ism-familiya juda uzun. 70 ta belgidan oshmasligi kerak."

    words = cleaned.split()
    if len(words) < 2:
        return False, "Iltimos, to'liq ism va familiyangizni kiriting (masalan: Ali Valiyev)."

    # Harflar (lotin, kirill), bo'shliq, chiziqcha va tutuq belgilari
    # O'zbek tilida: o', g', sh, ch kabi harflar va har xil apostroflar ishlatiladi
    pattern = r"^[a-zA-Zа-яА-ЯёЁ\s'\`’ʻʼ-]+$"
    if not re.match(pattern, cleaned):
        return False, "Ism-familiyada faqat harflar, bo'sh joy va tutuq belgilari bo'lishi mumkin."

    # Har bir so'z bosh harf bilan boshlanishi uchun formatlash
    formatted_name = " ".join(word.capitalize() for word in words)
    return True, formatted_name


def validate_and_normalize_phone(phone: str | None) -> Tuple[bool, str]:
    """Telefon raqamini tekshiradi va standart formatga (+998XXXXXXXXX) keltiradi.
    
    Qo'llab-quvvatlanadigan formatlar:
    - +998901234567
    - 998901234567
    - 901234567 (9 xonali lokal format)
    - +998 (90) 123-45-67 (bo'shliq, qavs, defislar bilan)
    
    Returns:
        Tuple[bool, str]: (to'g'ri_yoki_noto'g'ri, normalizatsiya_qilingan_raqam_yoki_xato_xabari)
    """
    if not phone or not isinstance(phone, str):
        return False, "Telefon raqami kiritilmadi. Iltimos, telefon raqamingizni kiriting."

    # Faqat raqamlar va boshidagi '+' belgisini qoldiramiz
    cleaned = phone.strip()
    digits_only = re.sub(r"\D", "", cleaned)

    if not digits_only:
        return False, "Telefon raqami noto'g'ri kiritildi. Faqat raqamlardan foydalaning."

    # O'zbekiston raqamlari tekshiruvi:
    # 1) Agar 9 xonali bo'lsa (masalan: 901234567) -> oldiga 998 qo'shamiz
    # 2) Agar 12 xonali bo'lsa va 998 bilan boshlansa -> to'g'ri
    if len(digits_only) == 9:
        normalized = f"+998{digits_only}"
    elif len(digits_only) == 12 and digits_only.startswith("998"):
        normalized = f"+{digits_only}"
    else:
        return (
            False,
            "Telefon raqami O'zbekiston formatida (+998) bo'lishi kerak.\n"
            "Masalan: +998901234567 yoki 90 123 45 67"
        )

    # 998 dan keyingi 2 ta raqam operator kodi (masalan, 90, 91, 93, 94, 95, 97, 98, 99, 88, 33, 77, 50, 55 va h.k.)
    valid_codes = {
        "33", "50", "55", "70", "71", "72", "73", "74", "75", "76",
        "77", "78", "79", "88", "90", "91", "93", "94", "95", "97",
        "98", "99"
    }
    operator_code = normalized[4:6]
    if operator_code not in valid_codes:
        return (
            False,
            f"'{operator_code}' operator kodi noto'g'ri. Iltimos, amaldagi O'zbekiston telefon raqamini kiriting."
        )

    return True, normalized
