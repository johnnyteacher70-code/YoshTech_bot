"""YoshTech Telegram Bot - Administrator paneli handleri.

Ushbu modulda administratorlar uchun /admin komandasi, statistika, arizalar ro'yxati,
CSV formatida yuklab olish va foydalanuvchilarga xabar tarqatish (broadcast) imkoniyatlari mavjud.
"""

import io
from datetime import datetime
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config import ADMIN_IDS, is_admin
from database import (
    get_all_applications,
    get_all_user_ids,
    get_recent_applications,
    get_statistics,
    update_application_status,
)
from keyboards.admin_menu import (
    get_admin_panel_keyboard,
    get_cancel_broadcast_keyboard,
)
from states.admin import AdminStates

admin_router = Router(name="admin_router")


@admin_router.message(Command("admin"))
async def handle_admin_command(message: Message, state: FSMContext) -> None:
    """/admin buyrug'i: Faqat administratorlar uchun panelni ochadi."""
    if not is_admin(message.from_user.id if message.from_user else None):
        return

    await state.clear()
    text = (
        "👑 <b>YoshTech Administrator Paneli</b>\n\n"
        "Quyidagi tugmalar orqali bot statistikasi, tushgan arizalar va "
        "boshqaruv imkoniyatlaridan foydalanishingiz mumkin:"
    )
    await message.answer(text=text, reply_markup=get_admin_panel_keyboard())


@admin_router.callback_query(F.data == "admin:stats")
async def callback_admin_stats(callback: CallbackQuery) -> None:
    """Statistikani ko'rsatish."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    stats = await get_statistics()
    courses_text = ""
    if stats["courses_stats"]:
        for course_name, cnt in stats["courses_stats"]:
            courses_text += f"  • {course_name}: <b>{cnt} ta</b>\n"
    else:
        courses_text = "  <i>(Hozircha arizalar yo'q)</i>\n"

    text = (
        "📊 <b>YoshTech Bot Statistikasi:</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']} nafar\n"
        f"📋 <b>Jami arizalar:</b> {stats['total_applications']} ta\n"
        f"⚡ <b>Bugungi arizalar:</b> {stats['today_applications']} ta\n\n"
        f"🎯 <b>Kurslar bo'yicha arizalar:</b>\n{courses_text}"
    )

    if callback.message:
        await callback.message.edit_text(text=text, reply_markup=get_admin_panel_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:recent")
async def callback_admin_recent(callback: CallbackQuery) -> None:
    """So'nggi arizalar ro'yxatini ko'rsatish."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    recent_apps = await get_recent_applications(limit=7)

    if not recent_apps:
        text = (
            "📋 <b>Oxirgi arizalar:</b>\n\n"
            "<i>Hozircha bazada birorta ham ariza mavjud emas.</i>"
        )
    else:
        text = "📋 <b>Oxirgi kelib tushgan arizalar:</b>\n\n"
        for app in recent_apps:
            username_str = f"@{app['username']}" if app['username'] else "Mavjud emas"
            status_emoji = "🟡 Yangi" if app['status'] == "yangi" else ("🟢 Bog'lanildi" if app['status'] == "boglanildi" else "🔴 Bekor")
            text += (
                f"<b>#{app['id']} | {app['full_name']}</b>\n"
                f"📞 {app['phone_number']} | 🎯 {app['course']}\n"
                f"✈️ {username_str} | 📅 {app['created_at']}\n"
                f"Holati: {status_emoji}\n"
                "────────────────────\n"
            )

    if callback.message:
        await callback.message.edit_text(text=text, reply_markup=get_admin_panel_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin:status:"))
async def callback_change_app_status(callback: CallbackQuery) -> None:
    """Adminga kelgan ariza bildirishnomasidagi statusni o'zgartirish."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    parts = callback.data.split(":")
    app_id = int(parts[2])
    new_status = parts[3]

    await update_application_status(app_id, new_status)

    status_name = "Bog'lanildi ✅" if new_status == "boglanildi" else "Bekor qilindi ❌"
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(f"Ariza #{app_id} holati yangilandi: <b>{status_name}</b>")

    await callback.answer(f"Status: {status_name}")


@admin_router.callback_query(F.data == "admin:export")
async def callback_admin_export(callback: CallbackQuery) -> None:
    """Barcha arizalarni CSV fayl ko'rinishida yuklab olish."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    apps = await get_all_applications()

    if not apps:
        await callback.answer("Eksport qilish uchun arizalar mavjud emas.", show_alert=True)
        return

    # CSV fayl yaratish (Excel uchun UTF-8 BOM bilan)
    output = io.StringIO()
    output.write("\ufeff")  # UTF-8 BOM
    output.write("ID,Ism-Familiya,Telefon,Kurs,Telegram,Holati,Sana\n")

    for app in apps:
        uname = f"@{app['username']}" if app['username'] else "-"
        # Vergullarni almashtiramiz
        fname = app['full_name'].replace(",", " ")
        cname = app['course'].replace(",", " ")
        output.write(f"{app['id']},{fname},{app['phone_number']},{cname},{uname},{app['status']},{app['created_at']}\n")

    csv_bytes = output.getvalue().encode("utf-8")
    filename = f"yoshtech_arizalar_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    document = BufferedInputFile(csv_bytes, filename=filename)

    if callback.message:
        await callback.message.answer_document(
            document=document,
            caption="📥 Barcha arizalar ro'yxati (Excel yoki Google Sheets da ochish mumkin)."
        )

    await callback.answer()


@admin_router.callback_query(F.data == "admin:broadcast")
async def callback_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Xabar tarqatishni boshlash."""
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_broadcast)
    text = (
        "📢 <b>Barcha foydalanuvchilarga xabar yuborish:</b>\n\n"
        "Yubormoqchi bo'lgan xabaringizni (matn, rasm, havola) yozing. "
        "Ushbu xabar botga kirgan barcha foydalanuvchilarga jo'natiladi.\n\n"
        "<i>Bekor qilish uchun quyidagi tugmani bosing:</i>"
    )

    if callback.message:
        await callback.message.answer(text=text, reply_markup=get_cancel_broadcast_keyboard())
    await callback.answer()


@admin_router.callback_query(F.data == "admin:cancel_broadcast")
async def callback_cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Xabar tarqatishni bekor qilish."""
    await state.clear()
    if callback.message:
        await callback.message.delete()
        await callback.message.answer(
            text="Xabar tarqatish bekor qilindi.",
            reply_markup=get_admin_panel_keyboard(),
        )
    await callback.answer()


@admin_router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    """Admin kiritgan xabarni barcha foydalanuvchilarga tarqatadi."""
    if not is_admin(message.from_user.id if message.from_user else None):
        return

    user_ids = await get_all_user_ids()
    await state.clear()

    if not user_ids:
        await message.answer("Bazada birorta ham foydalanuvchi mavjud emas.")
        return

    progress_msg = await message.answer(f"⏳ Xabar {len(user_ids)} nafar foydalanuvchiga yuborilmoqda...")

    success_count = 0
    fail_count = 0

    for user_id in user_ids:
        try:
            await message.send_copy(chat_id=user_id)
            success_count += 1
        except Exception:
            fail_count += 1

    await progress_msg.edit_text(
        f"✅ <b>Xabar tarqatish yakunlandi!</b>\n\n"
        f"• Yetib bordi: <b>{success_count}</b> ta\n"
        f"• Yetib bormadi (bloklaganlar): <b>{fail_count}</b> ta",
        reply_markup=get_admin_panel_keyboard()
    )


@admin_router.callback_query(F.data == "admin:close")
async def callback_admin_close(callback: CallbackQuery) -> None:
    """Panelni yopish."""
    if callback.message:
        await callback.message.delete()
    await callback.answer("Admin panel yopildi.")
