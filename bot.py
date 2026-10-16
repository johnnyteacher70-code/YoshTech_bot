"""YoshTech Telegram Bot - Asosiy kirish nuqtasi (Entry Point).

Ushbu fayl botni sozlaydi, barcha routerlarni ro'yxatdan o'tkazadi,
FSM xotirasini ulaydi va long polling rejimida botni ishga tushiradi.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
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

import os
from aiohttp import web

# Log yozishni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("yoshtech_bot")


async def start_health_server() -> web.AppRunner | None:
    """Render kabi bulutli platformalar uchun engil HTTP health server ishga tushiradi.
    
    Agar PORT muhit o'zgaruvchisi berilgan bo'lsa (Render avtomatik beradi),
    veb-server ishga tushadi va Render botni sog'lom (Healthy) deb baholaydi.
    """
    port_str = os.getenv("PORT")
    if not port_str:
        return None

    try:
        port = int(port_str)
    except ValueError:
        return None

    app = web.Application()

    async def handle_ping(request: web.Request) -> web.Response:
        return web.Response(text="YoshTech Bot 24/7 faol rejimda!")

    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info("Render platformasi uchun HTTP server ishga tushirildi (Port: %s).", port)
    return runner


async def main() -> None:
    """Botning asosiy asinxron ishga tushirish funksiyasi."""
    logger.info("YoshTech bot konfiguratsiyasi tekshirilmoqda...")

    # Konfiguratsiyani tekshirish
    try:
        bot_token = validate_config()
    except ValueError as exc:
        logger.error(str(exc))
        return

    logger.info("Bot obyekti yaratilmoqda...")
    # HTML parse mode bilan bot obyektini yaratish
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # In-memory FSM storage bilan Dispatcher yaratish
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Barcha routerlarni tartib bilan ulash
    dp.include_router(start_router)
    dp.include_router(courses_router)
    dp.include_router(registration_router)
    dp.include_router(about_router)
    dp.include_router(contact_router)
    # fallback_router eng oxirida ulanishi shart (noma'lum xabarlar uchun)
    dp.include_router(fallback_router)

    logger.info("Barcha routerlar Dispatcherga muvaffaqiyatli ulandi.")

    # Render yoki boshqa platformalar uchun HTTP serverni ishga tushirish (PORT bo'lsa)
    web_runner = await start_health_server()

    try:
        # Eski kutilayotgan yangilanishlarni (updates) tozalash va pollingni boshlash
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Long polling ishga tushmoqda. Bot faol holatda!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as exc:
        logger.exception("Bot ishlashida kutilmagan xatolik yuz berdi: %s", exc)
    finally:
        if web_runner:
            logger.info("HTTP health server to'xtatilmoqda...")
            await web_runner.cleanup()
        logger.info("Bot sessiyasi yopilmoqda...")
        await bot.session.close()
        logger.info("Bot muvaffaqiyatli to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi (Ctrl+C).")
