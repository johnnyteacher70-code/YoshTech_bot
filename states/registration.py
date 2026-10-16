"""YoshTech Telegram Bot - Kursga yozilish FSM holatlari.

Foydalanuvchi ma'lumotlarini qadamma-qadam to'plash uchun aiogram FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Kursga ro'yxatdan o'tish bosqichlari."""
    full_name = State()       # Talabaning ism va familiyasi
    phone_number = State()    # Bog'lanish uchun telefon raqami
    course = State()          # Tanlangan o'quv kursi
    confirmation = State()    # Ma'lumotlarni tekshirish va tasdiqlash
