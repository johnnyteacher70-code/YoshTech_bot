"""YoshTech bot handlerlari to'plami."""

from .start import start_router
from .courses import courses_router
from .registration import registration_router
from .about import about_router
from .contact import contact_router
from .fallback import fallback_router

__all__ = [
    "start_router",
    "courses_router",
    "registration_router",
    "about_router",
    "contact_router",
    "fallback_router",
]
