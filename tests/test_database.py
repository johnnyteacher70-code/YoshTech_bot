"""YoshTech Telegram Bot - Ma'lumotlar bazasi testlari."""

import asyncio
from database import (
    init_db,
    upsert_user,
    add_application,
    get_statistics,
    get_recent_applications,
    get_all_applications,
    get_all_user_ids,
    update_application_status,
    delete_application,
)


def test_database_crud_operations():
    async def _test():
        # 1. Initsializatsiya
        await init_db()

        # 2. Foydalanuvchini qo'shish / yangilash
        test_uid = 999888777
        await upsert_user(user_id=test_uid, username="test_user", full_name="Test User")
        user_ids = await get_all_user_ids()
        assert test_uid in user_ids

        # 3. Yangi ariza qo'shish
        app_id = await add_application(
            user_id=test_uid,
            username="test_user",
            full_name="Test User",
            phone_number="+998901234567",
            course="Python dasturlash",
        )
        assert app_id > 0

        # 4. Statistikani tekshirish
        stats = await get_statistics()
        assert stats["total_users"] >= 1
        assert stats["total_applications"] >= 1

        # 5. Oxirgi arizalarni olish
        recent = await get_recent_applications(limit=5)
        assert any(a["id"] == app_id for a in recent)

        # 6. Statusni yangilash
        updated = await update_application_status(app_id=app_id, status="boglanildi")
        assert updated is True

        # 7. Arizani o'chirish
        deleted = await delete_application(app_id=app_id)
        assert deleted is True

    asyncio.run(_test())
