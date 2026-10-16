"""YoshTech Telegram Bot - Administrator FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Admin amallari uchun holatlar."""
    waiting_for_broadcast = State()  # Barcha foydalanuvchilarga yuboriladigan xabar
