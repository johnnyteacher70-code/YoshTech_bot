# YoshTech Telegram Boti — O'quv Markazi Demo Boti

Ushbu loyiha zamonaviy axborot texnologiyalari va dasturlashga ixtisoslashgan to'qima **YoshTech** o'quv markazi uchun tayyorlangan ko'rgazmali (demo) Telegram bot hisoblanadi. Bot **Python 3.11+** va eng so'nggi barqaror **aiogram 3.x** freymvorki asosida to'liq asinxron arxitekturada qurilgan.

---

## 📋 Mundarija

1. [Loyiha haqida](#loyiha-haqida)
2. [Asosiy imkoniyatlar](#asosiy-imkoniyatlar)
3. [Texnologiyalar steki](#texnologiyalar-steki)
4. [Loyiha tuzilishi](#loyiha-tuzilishi)
5. [Fayllar tavsifi va vazifalari](#fayllar-tavsifi-va-vazifalari)
6. [Tizim talablari (Prerequisites)](#tizim-talablari-prerequisites)
7. [BotFather orqali bot tokenini olish](#botfather-orqali-bot-tokenini-olish)
8. [O'rnatish va ishga tushirish (Windows)](#ornatish-va-ishga-tushirish-windows)
9. [Botni sinovdan o'tkazish (Test qo'llanmasi)](#botni-sinovdan-otkazish-test-qollanmasi)
10. [Keng tarqalgan xatoliklar va yechimlar](#keng-tarqalgan-xatoliklar-va-yechimlar)
11. [Botni to'xtatish](#botni-toxtatish)
12. [Demo versiya cheklovlari va kelgusidagi rejalar](#demo-versiya-cheklovlari-va-kelgusidagi-rejalar)

---

## 🌟 Loyiha haqida

**YoshTech Telegram Boti** foydalanuvchilarga o'quv markazi faoliyati, taqdim etilayotgan kurslar haqida batafsil ma'lumot olish hamda qiziqqan kursiga ro'yxatdan o'tish imkoniyatini taqdim etadi.

Loyihaning asosiy maqsadi — toza, modulli, o'qilishi oson va boshlovchi Python dasturchilari o'rganishi uchun qulay namunaviy arxitekturani namoyish etishdir.

---

## 🚀 Asosiy imkoniyatlar

- **Xush kelibsiz xabari va doimiy menyu:** Foydalanuvchini ismi bilan qutlash (`/start`) va qulay `ReplyKeyboardMarkup` menyusi.
- **Batafsil kurslar katalogi:** 5 ta asosiy yo'nalish bo'yicha to'liq ma'lumot:
  1. *Frontend dasturlash*
  2. *Python dasturlash*
  3. *Kompyuter savodxonligi*
  4. *Grafik dizayn*
  5. *Robototexnika*
- **Har bir kursdan to'g'ridan-to'g'ri yozilish:** Kurs sahifasidan chiqmasdan ariza topshirishni boshlash.
- **Ko'p bosqichli ro'yxatdan o'tish (FSM):** Ism-familiya, telefon raqami (kontakt tugmasi yoki qo'lda kiritish) va tanlangan kurs.
- **Aqlli ma'lumotlar validatsiyasi:** O'zbekiston telefon raqamlari formatlarini (`+998`, `90 123 45 67`, va boshqalar) tozalash va normalizatsiya qilish, ism-familiyadagi o'zbekcha harflar va tutuq belgilarini to'g'ri qabul qilish.
- **Arizani tasdiqlash va bekor qilish:** Ma'lumotlar xulosasini ko'rsatish, istalgan bosqichda `/cancel` yoki `❌ Bekor qilish` imkoniyati.
- **Markaz haqida va aloqa bo'limlari:** Shaffof va qulay tahrirlanuvchi ma'lumotlar.
- **Noma'lum xabarlarga javob (Fallback):** Tushunarsiz buyruq yoki xabarlarga muloyim yo'naltiruvchi javob.

---

## 🛠 Texnologiyalar steki

- **Python:** 3.11 yoki undan yangi versiya (Python 3.13 qo'llab-quvvatlanadi).
- **aiogram:** 3.x (Asinxron Telegram Bot freymvorki, Router va FSM).
- **python-dotenv:** Muhit o'zgaruvchilarini (`.env`) xavfsiz yuklash.
- **pytest:** Avtomatlashtirilgan test sinovlari.

---

## 📁 Loyiha tuzilishi

```text
yoshTech bot/
│
├── bot.py                  # Dasturning asosiy kirish nuqtasi (Entry Point)
├── config.py               # Muhit o'zgaruvchilari va token tekshiruvi
├── requirements.txt        # Kerakli Python kutubxonalari ro'yxati
├── .env.example            # Konfiguratsiya andozasi
├── .env                    # Maxfiy tokenlar fayli (Git'ga yuklanmaydi)
├── .gitignore              # Git e'tibor bermaydigan fayllar ro'yxati
├── README.md               # Loyiha hujjatlari (ushbu qo'llanma)
│
├── handlers/               # Xabarlar va hodisalarni qayta ishlovchi modullar
│   ├── __init__.py         # Barcha routerlarni eksport qiluvchi fayl
│   ├── start.py            # /start, /help, /menu komandalari
│   ├── courses.py          # Kurslar ro'yxati va tavsiflari
│   ├── registration.py     # Kursga ro'yxatdan o'tish (FSM dialogi)
│   ├── about.py            # Markaz haqida ma'lumot
│   ├── contact.py          # Aloqa va manzil ma'lumotlari
│   └── fallback.py         # Kutilmagan va noma'lum xabarlar uchun javob
│
├── keyboards/              # Klaviaturani shakllantiruvchi modullar
│   ├── __init__.py         # Klaviaturani eksport qiluvchi fayl
│   ├── main_menu.py        # Asosiy reply menyusi
│   └── course_menu.py      # Kurslar, tasdiqlash va kontakt inline/reply klaviaturalari
│
├── states/                 # aiogram FSM holatlari
│   ├── __init__.py         # Holatlarni eksport qiluvchi fayl
│   └── registration.py     # RegistrationStates klassi
│
├── utils/                  # Yordamchi vositalar
│   ├── __init__.py         # Yordamchi modullarni eksport qiluvchi fayl
│   └── validators.py       # Ism va telefon raqami validatsiyasi
│
└── tests/                  # Avtomatlashtirilgan unit testlar
    ├── __init__.py
    └── test_bot.py         # Validatsiya va router integratsiyasi testlari
```

---

## 🧩 Fayllar tavsifi va vazifalari

- `bot.py`: Telegram Bot va Dispatcher obyektlarini yaratadi, barcha routerlarni ulaydi, MemoryStorage xotira omborini sozlaydi va `dp.start_polling()` orqali xabarlarni qabul qilishni boshlaydi.
- `config.py`: `.env` faylidan `BOT_TOKEN`ni xavfsiz yuklaydi. Token kiritilmagan yoki namuna ko'rinishida bo'lsa, xatolik berib, dasturni xavfsiz to'xtatadi.
- `handlers/start.py`: Foydalanuvchi botni boshlaganda (`/start`), yordam so'raganda (`/help`) yoki menyuni chaqirganda (`/menu`) xush kelibsiz xabarlarini chiqaradi.
- `handlers/courses.py`: 5 ta o'quv kursi haqidagi batafsil ma'lumotlarni chiqaradi va kurs ichidan to'g'ridan-to'g'ri ariza topshirish tugmasini boshqaradi.
- `handlers/registration.py`: Ro'yxatdan o'tish qadamlarini (ism -> telefon -> kurs -> tasdiqlash) boshqaruvchi FSM dialogi.
- `handlers/about.py`: YoshTech o'quv markazi maqsadi va vazifalari haqida ma'lumot beradi.
- `handlers/contact.py`: Bog'lanish telefon raqami, Telegram manzili va manzil namunalarini ko'rsatadi.
- `handlers/fallback.py`: Foydalanuvchi menyudan tashqari tasodifiy matn yozganda muloyimlik bilan menyuga yo'naltiradi.
- `keyboards/main_menu.py`: Pastki doimiy menyu tugmalarini (`📚 Kurslar`, `📝 Kursga yozilish`, `🏫 Markaz haqida`, `📞 Aloqa`) shakllantiradi.
- `keyboards/course_menu.py`: Kurslarni ko'rish va ro'yxatdan o'tishdagi barcha inline va kontakt ulashish tugmalarini yaratadi.
- `states/registration.py`: FSM holatlarini (`full_name`, `phone_number`, `course`, `confirmation`) saqlovchi guruh.
- `utils/validators.py`: Foydalanuvchi kiritgan ism-familiya va telefon raqamini tekshirib, standart formatga keltiruvchi toza funksiyalar.

---

## ⚙️ Tizim talablari (Prerequisites)

- Operatsion tizim: Windows 10/11 (yoki Linux/macOS).
- Python: **3.11** yoki undan yuqori versiya.
- Internetga ulanish.

---

## 🤖 BotFather orqali bot tokenini olish

1. Telegram dasturida [@BotFather](https://t.me/BotFather) rasmiy botini oching.
2. `/newbot` buyrug'ini yuboring.
3. Botingiz uchun nom kiriting (Masalan: `YoshTech Demo Bot`).
4. Botingiz uchun yagona username tanlang (oxiri `bot` bilan tugashi shart, masalan: `yoshtech_demo_robot`).
5. BotFather sizga API Token beradi (Masalan: `7123456789:AAH...`).
6. Ushbu tokenni nusxalab oling.

---

## 💻 O'rnatish va ishga tushirish (Windows)

Loyiha papkasini oching va buyruqlar satri (PowerShell yoki Command Prompt) orqali quyidagi amallarni bajaring:

### 1. PowerShell orqali ishga tushirish (Tavsiya etiladi)

```powershell
# 1. Virtual muhit (venv) yaratish:
py -m venv .venv

# 2. Virtual muhitni faollashtirish (PowerShell):
.\.venv\Scripts\Activate.ps1

# Agar PowerShell skriptlarni ishga tushirishni bloklasa, ruxsat bering:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Kerakli kutubxonalarni o'rnatish:
python -m pip install -r requirements.txt

# 4. .env fayliga BotFather bergan tokenni joylashtirish:
# Loyiha papkasidagi .env faylini oching va quyidagicha yozing:
# BOT_TOKEN=BotFather_bergan_tokeningiz

# 5. Botni ishga tushirish:
python bot.py
```

### 2. Windows Command Prompt (CMD) orqali ishga tushirish

```cmd
:: 1. Virtual muhit yaratish:
py -m venv .venv

:: 2. Virtual muhitni faollashtirish:
.venv\Scripts\activate.bat

:: 3. Kutubxonalarni o'rnatish:
python -m pip install -r requirements.txt

:: 4. Botni ishga tushirish:
python bot.py
```

---

## 🧪 Botni sinovdan o'tkazish (Test qo'llanmasi)

### Avtomatlashtirilgan unit testlarni ishga tushirish:
Loyihada validatsiya va arxitektura butunligini tekshirish uchun testlar yozilgan. Ularni ishga tushirish:

```bash
python -m pytest
```

### Telegram interfeysi orqali tekshirish:
1. Telegramda botingizga kiring va `/start` buyrug'ini bosing.
   - *Kutilgan natija:* Sizning ismingiz bilan kutib oladi va pastda 4 ta asosiy tugma paydo bo'ladi.
2. `📚 Kurslar` tugmasini bosing:
   - 5 ta kurs inline ko'rinishida chiqadi. Har birini bosib ko'ring, uning tavsifi, foydalari va `📝 Shu kursga yozilish` tugmasi chiqadi.
3. `📝 Shu kursga yozilish` tugmasini bosing:
   - Kurs avtomatik tanlanadi va bot sizdan to'liq ism-familiyangizni so'raydi.
4. Noto'g'ri ism yozib ko'ring (Masalan: `Ali` yoki `12345`):
   - Bot xatolikni ko'rsatib, to'g'ri ism-familiya kiritishni so'raydi.
5. To'g'ri ism kiriting (Masalan: `Ali Valiyev`):
   - Bot telefon raqamini so'raydi va `📱 Telefon raqamni yuborish` tugmasini chiqaradi.
6. Telefon raqamingizni kontakt tugmasi orqali yuboring yoki qo'lda kiriting (Masalan: `90 123 45 67`):
   - Raqam avtomatik ravishda `+998901234567` formatiga keltiriladi.
7. Ma'lumotlar xulosasi paydo bo'ladi:
   - `✅ Tasdiqlash` tugmasini bosing -> Ariza demo rejimida qabul qilingani haqida bildirishnoma beriladi va FSM tozalangan holda asosiy menyuga qaytaradi.
8. `❌ Bekor qilish` yoki `/cancel` buyrug'ini sinab ko'ring:
   - Ro'yxatdan o'tish bekor qilinadi.
9. `🏫 Markaz haqida` va `📞 Aloqa` tugmalarini bosing:
   - Mos bo'lim ma'lumotlari to'g'ri ko'rinadi.
10. Botga ixtiyoriy matn (masalan, `Salom do'stim`) yuboring:
    - Fallback handleri ishga tushib, menyudan foydalanishni taklif qiladi.

---

## ⚠️ Keng tarqalgan xatoliklar va yechimlar

1. **XATOLIK: Telegram Bot Tokeni topilmadi yoki noto'g'ri sozlangan!**
   - **Sabab:** `.env` faylida token ko'rsatilmagan yoki namuna ko'rinishida qolib ketgan.
   - **Yechim:** `.env` faylini matn muharririda oching va `BOT_TOKEN=...` qatoriga o'z botingiz tokenini kiriting.

2. **PowerShell script execution policy xatoligi:**
   - **Sabab:** Windows PowerShell xavfsizlik sababli skriptlar ijrosini cheklagan.
   - **Yechim:** `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` buyrug'ini bajaring va venv'ni qayta faollashtiring.

3. **Unauthorized / Invalid Token:**
   - **Sabab:** Telegram BotFather bergan token noto'g'ri yoki bekor qilingan.
   - **Yechim:** BotFatherni tekshiring va yangi token olib `.env` ga yozing.

---

## 🛑 Botni to'xtatish

Bot konsolida ishlayotgan paytda uni to'xtatish uchun klaviaturada **`Ctrl + C`** tugmalarini bosing. Dastur bot sessiyasini xavfsiz va toza yopadi:
```text
INFO - yoshtech_bot - Bot sessiyasi yopilmoqda...
INFO - yoshtech_bot - Bot muvaffaqiyatli to'xtatildi.
```

---

## 📌 Demo versiya cheklovlari va kelgusidagi rejalar

### Joriy cheklovlar:
- **Ma'lumotlar bazasi mavjud emas:** Bu ko'rgazmali demo loyiha bo'lgani sababli, ro'yxatdan o'tgan foydalanuvchilar ma'lumotlari xotirada saqlanadi va server o'chirilganda tozalanadi.
- **Admin panel yo'q:** Arizalar administratorlarga yuborilmaydi (foydalanuvchiga bu demo ekanligi ochiq bildiriladi).

### Kelgusida kengaytirish bo'yicha tavsiyalar:
1. **Ma'lumotlar bazasi integratsiyasi:** PostgreSQL yoki SQLite (SQLAlchemy yoki Tortoise-ORM yordamida) ulab, talabalar arizalarini saqlash.
2. **Admin bildirishnomalari:** Yangi ariza tushganda o'quv markazi ma'murlariga Telegram orqali xabar yuborish.
3. **To'lov tizimlari:** Payme yoki Click provayderlari orqali kurslar uchun to'lov qabul qilish.
4. **Web dashboard:** Markaz xodimlari uchun arizalarni boshqaruvchi veb interfeys.
