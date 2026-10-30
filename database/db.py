"""YoshTech Telegram Bot - Ma'lumotlar bazasi moduli (PostgreSQL & SQLite gibrid).

Ushbu modul agar `DATABASE_URL` muhit o'zgaruvchisi berilgan bo'lsa (masalan, Supabase,
Neon.tech, Render Postgres), yuqori unumli asinxron `asyncpg` orqali PostgreSQL bazasiga ulanadi.
Agar `DATABASE_URL` mavjud bo'lmasa, avtomatik ravishda lokal `yoshtech.db` (SQLite) fayliga tushadi.
"""

from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.parse

import aiosqlite

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore

from config import DATABASE_URL

logger = logging.getLogger("yoshtech_bot.database")
DB_PATH = Path(__file__).resolve().parent.parent / "yoshtech.db"

_pg_pool: Optional[Any] = None


def is_postgres_configured() -> bool:
    """PostgreSQL URL sozlanganligi va asyncpg mavjudligini tekshiradi."""
    return bool(DATABASE_URL and DATABASE_URL.strip() and asyncpg is not None)


def _prepare_pg_dsn_and_ssl(raw_url: str) -> tuple[str, dict[str, Any]]:
    """PostgreSQL DSN manzilini tozalab, kerakli SSL parametrlarini ajratadi."""
    url = raw_url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)

    connect_kwargs: dict[str, Any] = {}
    netloc_lower = parsed.netloc.lower()

    # Masofaviy bulutli bazalar (Supabase, Neon, Render) uchun SSL talab qilinadi
    is_cloud_db = any(domain in netloc_lower for domain in ("supabase.co", "render.com", "neon.tech", "pooler.supabase.com"))
    if is_cloud_db or "sslmode" in query_params:
        connect_kwargs["ssl"] = "require"

    # asyncpg dsn ichidagi 'sslmode' query parametrini qabul qilmaydi, uni tozalaymiz
    clean_query = {k: v for k, v in query_params.items() if k != "sslmode"}
    clean_query_str = urllib.parse.urlencode(clean_query, doseq=True)
    clean_dsn = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query_str,
        parsed.fragment,
    ))

    return clean_dsn, connect_kwargs


async def get_pg_pool() -> Any:
    """PostgreSQL ulanishlar pulini (Connection Pool) oladi yoki yaratadi."""
    global _pg_pool
    if _pg_pool is None:
        dsn, kwargs = _prepare_pg_dsn_and_ssl(DATABASE_URL)
        logger.info("PostgreSQL (Supabase/Cloud) ulanishlar puli yaratilmoqda...")
        _pg_pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=1,
            max_size=10,
            command_timeout=60,
            **kwargs,
        )
        logger.info("PostgreSQL ulanishlar puli muvaffaqiyatli ishga tushdi.")
    return _pg_pool


async def close_db() -> None:
    """Ma'lumotlar bazasi ulanishlarini xavfsiz yopadi."""
    global _pg_pool
    if _pg_pool is not None:
        logger.info("PostgreSQL ulanishlar puli yopilmoqda...")
        await _pg_pool.close()
        _pg_pool = None


async def init_db() -> None:
    """Ma'lumotlar bazasi jadvallarini yaratadi (PostgreSQL yoki SQLite)."""
    if is_postgres_configured():
        logger.info("Doimiy PostgreSQL ma'lumotlar bazasi jadvallari tekshirilmoqda...")
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            # Foydalanuvchilar jadvali (user_id Telegram uchun BIGINT bo'lishi shart)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    created_at TEXT
                );
            """)

            # Arizalar jadvali
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    username TEXT,
                    full_name TEXT,
                    phone_number TEXT,
                    course TEXT,
                    status TEXT DEFAULT 'yangi',
                    created_at TEXT
                );
            """)
        logger.info("PostgreSQL jadvallari tayyor (users, applications).")
        return

    # Agar DATABASE_URL bo'lmasa, SQLite'dan foydalanish
    logger.info("Lokal SQLite ma'lumotlar bazasi ishlatilmoqda: %s", DB_PATH.name)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                phone_number TEXT,
                course TEXT,
                status TEXT DEFAULT 'yangi',
                created_at TEXT
            )
        """)
        await db.commit()


async def upsert_user(user_id: int, username: Optional[str], full_name: str) -> None:
    """Foydalanuvchini bazaga qo'shadi yoki mavjud bo'lsa yangilaydi."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, full_name, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    full_name = EXCLUDED.full_name
            """, user_id, username, full_name, now)
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, full_name, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
        """, (user_id, username, full_name, now))
        await db.commit()


async def add_application(
    user_id: int,
    username: Optional[str],
    full_name: str,
    phone_number: str,
    course: str
) -> int:
    """Yangi arizani bazaga saqlaydi va ariza ID raqamini qaytaradi."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            app_id = await conn.fetchval("""
                INSERT INTO applications (user_id, username, full_name, phone_number, course, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, user_id, username, full_name, phone_number, course, now)
            return int(app_id) if app_id else 0

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO applications (user_id, username, full_name, phone_number, course, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, full_name, phone_number, course, now))
        await db.commit()
        return cursor.lastrowid or 0


async def get_statistics() -> Dict[str, Any]:
    """Admin uchun umumiy statistikani hisoblaydi."""
    today_str = datetime.now().strftime("%Y-%m-%d")

    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            total_users = (await conn.fetchval("SELECT COUNT(*) FROM users")) or 0
            total_apps = (await conn.fetchval("SELECT COUNT(*) FROM applications")) or 0
            today_apps = (await conn.fetchval(
                "SELECT COUNT(*) FROM applications WHERE created_at LIKE $1",
                f"{today_str}%",
            )) or 0

            courses_rows = await conn.fetch("""
                SELECT course, COUNT(*) as cnt
                FROM applications
                GROUP BY course
                ORDER BY cnt DESC
            """)
            courses_stats = [(r["course"], r["cnt"]) for r in courses_rows]

            status_rows = await conn.fetch("""
                SELECT status, COUNT(*) as cnt
                FROM applications
                GROUP BY status
            """)
            status_stats = {r["status"]: r["cnt"] for r in status_rows}

        return {
            "total_users": total_users,
            "total_applications": total_apps,
            "today_applications": today_apps,
            "courses_stats": courses_stats,
            "status_stats": status_stats,
        }

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM applications") as cursor:
            total_apps = (await cursor.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM applications WHERE created_at LIKE ?",
            (f"{today_str}%",),
        ) as cursor:
            today_apps = (await cursor.fetchone())[0]

        async with db.execute("""
            SELECT course, COUNT(*) as cnt
            FROM applications
            GROUP BY course
            ORDER BY cnt DESC
        """) as cursor:
            courses_stats = await cursor.fetchall()

        async with db.execute("""
            SELECT status, COUNT(*) as cnt
            FROM applications
            GROUP BY status
        """) as cursor:
            raw_statuses = await cursor.fetchall()
            status_stats = {s: c for s, c in raw_statuses}

    return {
        "total_users": total_users,
        "total_applications": total_apps,
        "today_applications": today_apps,
        "courses_stats": courses_stats,
        "status_stats": status_stats,
    }


async def get_recent_applications(limit: int = 5) -> List[Dict[str, Any]]:
    """Oxirgi tushgan arizalarni qaytaradi."""
    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, user_id, username, full_name, phone_number, course, status, created_at
                FROM applications
                ORDER BY id DESC
                LIMIT $1
            """, limit)
            return [dict(r) for r in rows]

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, user_id, username, full_name, phone_number, course, status, created_at
            FROM applications
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_all_applications() -> List[Dict[str, Any]]:
    """Barcha arizalarni eksport qilish uchun qaytaradi."""
    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, user_id, username, full_name, phone_number, course, status, created_at
                FROM applications
                ORDER BY id DESC
            """)
            return [dict(r) for r in rows]

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, user_id, username, full_name, phone_number, course, status, created_at
            FROM applications
            ORDER BY id DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_all_user_ids() -> List[int]:
    """Barcha foydalanuvchilar ID ro'yxatini qaytaradi (xabar tarqatish uchun)."""
    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM users")
            return [int(r["user_id"]) for r in rows]

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def update_application_status(app_id: int, status: str) -> bool:
    """Ariza holatini (yangi, bog'lanildi, bekor_qilindi) yangilaydi."""
    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE applications
                SET status = $1
                WHERE id = $2
            """, status, app_id)
            return True

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE applications
            SET status = ?
            WHERE id = ?
        """, (status, app_id))
        await db.commit()
        return True


async def delete_application(app_id: int) -> bool:
    """Arizani bazadan o'chiradi."""
    if is_postgres_configured():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM applications WHERE id = $1", app_id)
            parts = result.split()
            count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            return count > 0

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        await db.commit()
        return (cursor.rowcount or 0) > 0
