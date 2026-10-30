"""YoshTech Telegram Bot - Gemini AI suhbati holatlari (FSM)."""

from aiogram.fsm.state import State, StatesGroup


class AIStates(StatesGroup):
    """AI bilan jonli muloqot holati."""

    chatting = State()
