"""YoshTech bot klaviaturalari to'plami."""

from .main_menu import get_main_menu_keyboard
from .course_menu import (
    get_courses_inline_keyboard,
    get_course_details_keyboard,
    get_course_selection_keyboard,
    get_phone_request_keyboard,
    get_confirmation_keyboard,
    get_cancel_reply_keyboard,
)

__all__ = [
    "get_main_menu_keyboard",
    "get_courses_inline_keyboard",
    "get_course_details_keyboard",
    "get_course_selection_keyboard",
    "get_phone_request_keyboard",
    "get_confirmation_keyboard",
    "get_cancel_reply_keyboard",
]
