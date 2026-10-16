"""YoshTech bot handlerlari to'plami."""

from .admin import admin_router
from .about import about_router
from .contact import contact_router
from .courses import courses_router
from .fallback import fallback_router
from .registration import registration_router
from .start import start_router

__all__ = [
    "admin_router",
    "start_router",
    "courses_router",
    "registration_router",
    "about_router",
    "contact_router",
    "fallback_router",
]
