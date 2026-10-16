"""YoshTech Telegram Bot - Veb boshqaruv paneli ilovasi (aiohttp).

Ushbu modul Render va boshqa platformalarda ishlaydigan engil va tezkor
veb-server hamda REST API ni taqdim etadi.
"""

import hashlib
import io
from datetime import datetime
from pathlib import Path
from aiohttp import web

from config import ADMIN_PASSWORD
from database import (
    delete_application,
    get_all_applications,
    get_statistics,
    update_application_status,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
DASHBOARD_HTML_PATH = TEMPLATES_DIR / "dashboard.html"


def generate_auth_token() -> str:
    """Admin parolidan xavfsiz token hosil qiladi."""
    return hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()[:32]


def is_authenticated(request: web.Request) -> bool:
    """So'rovning autentifikatsiyadan o'tganligini tekshiradi."""
    expected_token = generate_auth_token()

    # Query param orqali tekshirish (?token=...)
    token = request.query.get("token")
    if token and token == expected_token:
        return True

    # Header orqali tekshirish (Authorization: Bearer ...)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        header_token = auth_header.split("Bearer ")[1].strip()
        if header_token == expected_token:
            return True

    return False


async def handle_root(request: web.Request) -> web.Response:
    """Bosh sahifani /admin ga yo'naltiradi."""
    raise web.HTTPFound("/admin")


async def handle_health(request: web.Request) -> web.Response:
    """Render uchun sog'lomlik tekshiruvi (Health Check)."""
    return web.Response(text="YoshTech Bot & Web Dashboard is healthy 24/7!")


async def handle_admin_page(request: web.Request) -> web.Response:
    """Admin boshqaruv paneli HTML sahifasini uzatadi."""
    if not DASHBOARD_HTML_PATH.exists():
        return web.Response(text="Dashboard shabloni topilmadi.", status=404)

    html_content = DASHBOARD_HTML_PATH.read_text(encoding="utf-8")
    return web.Response(text=html_content, content_type="text/html")


async def handle_login(request: web.Request) -> web.Response:
    """Admin parolini tekshirib, token qaytaradi."""
    try:
        data = await request.json()
        password = data.get("password", "")
    except Exception:
        return web.json_response({"success": False, "error": "Noto'g'ri so'rov formati"}, status=400)

    if password == ADMIN_PASSWORD:
        token = generate_auth_token()
        return web.json_response({"success": True, "token": token})

    return web.json_response({"success": False, "error": "Parol noto'g'ri"}, status=401)


async def handle_api_stats(request: web.Request) -> web.Response:
    """Jonli statistikani JSON ko'rinishida qaytaradi."""
    if not is_authenticated(request):
        return web.json_response({"error": "Avtorizatsiyadan o'tilmagan"}, status=401)

    stats = await get_statistics()
    return web.json_response(stats)


async def handle_api_applications(request: web.Request) -> web.Response:
    """Barcha arizalar ro'yxatini JSON ko'rinishida qaytaradi."""
    if not is_authenticated(request):
        return web.json_response({"error": "Avtorizatsiyadan o'tilmagan"}, status=401)

    apps = await get_all_applications()
    return web.json_response(apps)


async def handle_api_update_status(request: web.Request) -> web.Response:
    """Ariza holatini yangilash (yangi, boglanildi, bekor)."""
    if not is_authenticated(request):
        return web.json_response({"error": "Avtorizatsiyadan o'tilmagan"}, status=401)

    try:
        app_id = int(request.match_info.get("id", 0))
        data = await request.json()
        new_status = data.get("status", "")
    except Exception:
        return web.json_response({"success": False, "error": "Noto'g'ri parametrlar"}, status=400)

    if new_status not in {"yangi", "boglanildi", "bekor"}:
        return web.json_response({"success": False, "error": "Noto'g'ri status"}, status=400)

    success = await update_application_status(app_id, new_status)
    return web.json_response({"success": success})


async def handle_api_delete_application(request: web.Request) -> web.Response:
    """Arizani bazadan o'chirish."""
    if not is_authenticated(request):
        return web.json_response({"error": "Avtorizatsiyadan o'tilmagan"}, status=401)

    app_id = int(request.match_info.get("id", 0))
    success = await delete_application(app_id)
    return web.json_response({"success": success})


async def handle_api_export_csv(request: web.Request) -> web.Response:
    """Arizalarni CSV (Excel) fayl ko'rinishida yuklab olish."""
    if not is_authenticated(request):
        return web.Response(text="Avtorizatsiyadan o'tilmagan. Qaytadan kiring.", status=401)

    apps = await get_all_applications()

    output = io.StringIO()
    output.write("\ufeff")  # UTF-8 BOM
    output.write("ID,Ism-Familiya,Telefon,Kurs,Telegram,Holati,Sana\n")

    for app in apps:
        uname = f"@{app['username']}" if app['username'] else "-"
        fname = (app['full_name'] or "").replace(",", " ")
        cname = (app['course'] or "").replace(",", " ")
        output.write(f"{app['id']},{fname},{app['phone_number']},{cname},{uname},{app['status']},{app['created_at']}\n")

    filename = f"yoshtech_arizalar_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }
    return web.Response(text=output.getvalue(), headers=headers)


async def handle_api_send_message(request: web.Request) -> web.Response:
    """Veb boshqaruv panelidan talabaning Telegramiga to'g'ridan-to'g'ri xabar yuborish."""
    if not is_authenticated(request):
        return web.json_response({"error": "Avtorizatsiyadan o'tilmagan"}, status=401)

    bot = request.app.get("bot")
    if not bot:
        return web.json_response({"success": False, "error": "Bot xizmati ulanmagan"}, status=500)

    try:
        data = await request.json()
        user_id = int(data.get("user_id", 0))
        message_text = str(data.get("message", "")).strip()
    except Exception:
        return web.json_response({"success": False, "error": "Noto'g'ri parametrlar"}, status=400)

    if not user_id or not message_text:
        return web.json_response({"success": False, "error": "Foydalanuvchi ID yoki xabar matni bo'sh"}, status=400)

    formatted_msg = (
        "📩 <b>YoshTech Ma'muriyatidan xabar:</b>\n\n"
        f"{message_text}\n\n"
        "<i>Savollaringiz bo'lsa, ushbu bot orqali bemalol javob yozishingiz mumkin.</i>"
    )

    try:
        await bot.send_message(chat_id=user_id, text=formatted_msg)
        return web.json_response({"success": True})
    except Exception as exc:
        return web.json_response({"success": False, "error": f"Xabar yuborilmadi: {exc}"}, status=500)


def create_web_application(bot=None) -> web.Application:
    """aiohttp web application yaratadi va marshrutlarni (routes) ulaydi."""
    app = web.Application()
    if bot:
        app["bot"] = bot

    # Sahifalar
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/admin", handle_admin_page)

    # API
    app.router.add_post("/api/login", handle_login)
    app.router.add_get("/api/stats", handle_api_stats)
    app.router.add_get("/api/applications", handle_api_applications)
    app.router.add_post("/api/applications/{id}/status", handle_api_update_status)
    app.router.add_delete("/api/applications/{id}", handle_api_delete_application)
    app.router.add_get("/api/export", handle_api_export_csv)
    app.router.add_post("/api/send-message", handle_api_send_message)

    return app
