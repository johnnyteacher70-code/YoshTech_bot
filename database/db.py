"""YoshTech Telegram Bot - Asinxron SQLite ma'lumotlar bazasi moduli.

Ushbu modulda foydalanuvchilar va o'quv kurslariga tushgan arizalarni saqlash,
statistika olish va administrator uchun ma'lumotlarni chiqarish funksiyalari mavjud.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiosqlite

DB_PATH = Path(__file__).resolve().parent.parent / "yoshtech.db"


async def init_db() -> None:
    """Ma'lumotlar bazasi jadvallarini yaratadi."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TEXT
            )
        """)

        # Arizalar jadvali
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

    async with aiosqlite.connect(DB_PATH) as db:
        # Jami foydalanuvchilar
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]

        # Jami arizalar
        async with db.execute("SELECT COUNT(*) FROM applications") as cursor:
            total_apps = (await cursor.fetchone())[0]

        # Bugungi arizalar
        async with db.execute(
            "SELECT COUNT(*) FROM applications WHERE created_at LIKE ?",
            (f"{today_str}%",)
        ) as cursor:
            today_apps = (await cursor.fetchone())[0]

        # Kurslar bo'yicha taqsimot
        async with db.execute("""
            SELECT course, COUNT(*) as cnt
            FROM applications
            GROUP BY course
            ORDER BY cnt DESC
        """) as cursor:
            courses_stats = await cursor.fetchall()

    return {
        "total_users": total_users,
        "total_applications": total_apps,
        "today_applications": today_apps,
        "courses_stats": courses_stats,
    }


async def get_recent_applications(limit: int = 5) -> List[Dict[str, Any]]:
    """Oxirgi tushgan arizalarni qaytaradi."""
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
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def update_application_status(app_id: int, status: str) -> bool:
    """Ariza holatini (yangi, bog'lanildi, bekor_qilindi) yangilaydi."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE applications
            SET status = ?
            WHERE id = ?
        """, (status, app_id))
        await db.commit()
        return True
