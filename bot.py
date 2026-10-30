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
from database import close_db, init_db
from handlers import (
    about_router,
    admin_router,
    ai_router,
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


from web import create_web_application


async def start_web_server(bot: Bot | None = None) -> web.AppRunner:
    """Render va mahalliy foydalanish uchun Veb Admin Dashboard va HTTP serverni ishga tushiradi."""
    port_str = os.getenv("PORT")
    port = int(port_str) if port_str and port_str.isdigit() else 8080

    app = create_web_application(bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info("Veb boshqaruv paneli (Web Admin Dashboard) faol: port %s (/admin)", port)
    return runner


async def keep_alive_background_task() -> None:
    """Render bepul tarifida bot uxlab qolmasligi uchun har 10 daqiqada o'zini ping qilib turadi."""
    external_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if not external_url:
        logger.info("RENDER_EXTERNAL_URL topilmadi. Self-ping ishga tushirilmadi (lokal rejim).")
        return

    health_url = f"{external_url.rstrip('/')}/health"
    logger.info("Render 24/7 Keep-Alive xizmati faollashdi: %s", health_url)

    # 3 daqiqadan so'ng birinchi ping
    await asyncio.sleep(180)
    import aiohttp
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(health_url, timeout=15) as resp:
                    logger.info("Render 24/7 Keep-Alive ping muvaffaqiyatli [HTTP %s]", resp.status)
            except Exception as exc:
                logger.warning("Render Keep-Alive ping xatosi: %s", exc)
            # Har 10 daqiqada (Render 15 daqiqada uxlaydi)
            await asyncio.sleep(600)


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

    # Ma'lumotlar bazasini initsializatsiya qilish
    logger.info("Ma'lumotlar bazasi tekshirilmoqda...")
    await init_db()

    # Barcha routerlarni tartib bilan ulash
    dp.include_router(start_router)
    dp.include_router(courses_router)
    dp.include_router(registration_router)
    dp.include_router(ai_router)
    dp.include_router(about_router)
    dp.include_router(contact_router)
    # Administrator paneli
    dp.include_router(admin_router)
    # fallback_router eng oxirida ulanishi shart (noma'lum xabarlar uchun)
    dp.include_router(fallback_router)

    logger.info("Barcha routerlar Dispatcherga muvaffaqiyatli ulandi.")

    # Render yoki boshqa platformalar uchun Veb Admin Dashboard va HTTP serverni ishga tushirish
    web_runner = await start_web_server(bot=bot)

    # 24/7 Render Keep-Alive fon vazifasini ishga tushirish
    keep_alive_task = asyncio.create_task(keep_alive_background_task())

    try:
        # Eski kutilayotgan yangilanishlarni (updates) tozalash va pollingni boshlash
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Long polling ishga tushmoqda. Bot faol holatda!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as exc:
        logger.exception("Bot ishlashida kutilmagan xatolik yuz berdi: %s", exc)
    finally:
        keep_alive_task.cancel()
        if web_runner:
            logger.info("HTTP health server to'xtatilmoqda...")
            await web_runner.cleanup()
        logger.info("Ma'lumotlar bazasi sessiyalari yopilmoqda...")
        await close_db()
        logger.info("Bot sessiyasi yopilmoqda...")
        await bot.session.close()
        logger.info("Bot muvaffaqiyatli to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi (Ctrl+C).")
