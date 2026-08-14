# Anki FlashFill — Project Status & Roadmap

> **راهنمای استمرار پروژه برای هوش مصنوعی‌های آینده**
> اگر این فایل را می‌خوانی، یعنی قرار است کار این پروژه را ادامه بدهی.
> تمام وضعیت جاری، فایل‌ها، و مراحل بعدی اینجا ثبت شده.

---

## 📋 هدف کلی پروژه

ساخت یک **Add-on برای Anki Desktop** با Python که برای ساخت فلشکارت‌های زبان، اطلاعات را به‌صورت خودکار تکمیل کند.

پروژه باید **مرحله‌ای و modular** باشد.

---

## 🗂️ ساختار فایل‌های پروژه

```
d:\Mehran\Anki add-on\           <- پوشه اصلی add-on (همین پوشه در Anki Addons قرار می‌گیرد)
|
├── __init__.py                   [DONE] Entry point + ساخت خودکار Note Type در اولین اجرا
├── config.json                   [DONE] Default config
├── config.md                     [DONE] مرجع کامل همه کلیدهای config
├── README.md                     [DONE] راهنمای کامل نصب و استفاده (انگلیسی)
├── GUIDE_FA.md                   [DONE] راهنمای کامل نصب و استفاده (فارسی)
├── PROJECT_STATUS.md             [DONE] این فایل — وضعیت پروژه
|
├── core/
|   ├── __init__.py               [DONE]
|   ├── models.py                 [DONE] LanguageData dataclass
|   ├── autofill.py               [DONE] منطق Auto Fill + Cache + Preview + Apply
|   ├── audio_fill.py             [DONE] منطق دانلود و ذخیره Audio در Media
|   ├── image_fill.py             [DONE] منطق دانلود و ذخیره Image در Media
|   └── cache.py                  [DONE] کش Session - جلوگیری از درخواست تکراری برای یک کلمه
|
├── providers/
|   ├── __init__.py               [DONE]
|   ├── base.py                   [DONE] BaseLanguageProvider (abstract class)
|   ├── mock.py                   [DONE] MockProvider - برای تست بدون API
|   ├── gemini_provider.py        [DONE] GeminiProvider - Google AI Studio
|   ├── openrouter_provider.py    [DONE] OpenRouterProvider - دسترسی به مدل‌های متعدد
|   └── audio/
|       ├── __init__.py           [DONE]
|       ├── base.py               [DONE] BaseAudioProvider (abstract class)
|       ├── gtts_provider.py      [DONE] GTTSProvider - Google Translate TTS (بدون API Key)
|       └── mock_audio.py         [DONE] MockAudioProvider - برای تست بدون شبکه
|
|   └── image/
|       ├── __init__.py           [DONE]
|       ├── base.py               [DONE] BaseImageProvider (abstract class)
|       ├── unsplash.py           [DONE] UnsplashProvider - Unsplash API (50 req/h رایگان)
|       ├── pexels.py             [DONE] PexelsProvider - Pexels API (200 req/h رایگان)
|       └── mock_image.py         [DONE] MockImageProvider - PNG آبی برای تست بدون شبکه
|
├── ui/
|   ├── __init__.py               [DONE]
|   ├── editor_btn.py             [DONE] دکمه‌های Auto Fill و Settings در Editor
|   ├── settings_dialog.py        [DONE] Settings Dialog (پنج تب: General, Provider, Audio, Image, Field Mapping)
|   └── preview_dialog.py         [DONE] Preview Dialog — نمایش داده‌ها قبل از اعمال
|
├── utils/
|   ├── __init__.py               [DONE]
|   └── logger.py                 [DONE] سیستم logging بدون ذخیره API Key
|
└── card_templates/               [EMPTY] آماده برای مراحل بعدی
```

---

## مرحله ۱ — Auto Fill اطلاعات زبان — COMPLETED

### وضعیت: تکمیل شده و قابل اجرا

### چه چیزی پیاده‌سازی شده:

**کارکرد اصلی:**
- کاربر یک کلمه یا عبارت در فیلد trigger (پیش‌فرض: Front) وارد می‌کند
- با کلیک روی دکمه "Auto Fill" در editor، اطلاعات زبانی به‌صورت خودکار دریافت و در فیلدهای Note قرار می‌گیرد
- میانبر کیبورد: Ctrl+Shift+A

**فیلدهایی که پر می‌شوند:**
- Translation — ترجمه فارسی (یا هر زبان target دیگری)
- English — ترجمه انگلیسی
- Pronunciation — تلفظ IPA
- Part of Speech — نوع کلمه
- Gender — جنسیت (در صورت وجود)
- Example — مثال در زبان source
- Example Translation — ترجمه مثال
- CEFR — سطح CEFR
- Notes — یادداشت‌های گرامری

**Provider Architecture (قابل تنظیم):**
- mock — بدون API، داده‌های نمونه برمی‌گرداند (برای تست)
- gemini — Google Gemini 1.5 Flash API
- openrouter — دسترسی به مدل‌های متعدد (شامل مدل‌های رایگان)

**Settings Dialog:**
- 3 تب: General / Provider / Field Mapping
- انتخاب زبان source و target از لیست
- تنظیم API Key (هرگز hard-code نمی‌شود)
- انتخاب مدل OpenRouter
- Test Connection با feedback زنده
- تنظیم field mapping (هر فیلد قابل تنظیم است)
- طراحی مدرن dark/glassmorphism با QSS

**ویژگی‌های فنی:**
- اگر فیلدی در Note وجود نداشت: خطا نمی‌دهد، رد می‌کند
- اگر فیلد قبلاً پر بود: overwrite نمی‌کند (محتوا حفظ می‌شود)
- Network operation بدون freeze کردن UI (از QueryOp و run_in_background استفاده می‌کند)
- Logging با get_logger بدون ذخیره API Key در لاگ

### نحوه نصب و تست:
1. این پوشه را در مسیر Anki addons قرار بده:
   Windows: C:\Users\<USER>\AppData\Roaming\Anki2\addons21\anki_language_autofill\
2. Anki را restart کن
3. یک Note با فیلدهای: Front, Translation, English, Pronunciation, Part of Speech, Gender, Example, Example Translation, CEFR, Notes بساز
4. در Settings - Provider را روی mock بگذار
5. کلمه "mucho gusto" یا "perro" را در فیلد Front بنویس و Auto Fill را بزن

---

## مرحله ۲ — تصویر خودکار — COMPLETED

### وضعیت: تکمیل شده و قابل اجرا

### چه چیزی پیاده‌سازی شده:

**کارکرد اصلی:**
- بر اساس ترجمه انگلیسی کلمه (از Stage 1)، یک Image Query مناسب تولید می‌شود
- تصویر از Provider دانلود و در Anki Media ذخیره می‌شود
- فیلد Image کارت با تگ <img src="filename"> پر می‌شود
- اگر دانلود fail شود، خطا فقط log می‌شود و بقیه فیلدها پر می‌شوند (non-fatal)

**Image Query Generation (هوشمند):**
- Noun: perro + english="dog" → query: "dog"
- Verb: comer + english="to eat" → query: "person eating"
- Phrase: mucho gusto + english="Nice to meet you" → query: "Nice to meet you two people"

**Image Providers:**
- mock — PNG آبی 60×60 پیکسلی برای تست (بدون شبکه، با struct+zlib ساخته شده)
- unsplash — Unsplash API (رایگان، نیاز به Access Key، 50 req/h)
- pexels — Pexels API (رایگان، نیاز به API Key، 200 req/h)

**فایل‌های ایجاد/بروزرسانی‌شده:**
- providers/image/__init__.py — پکیج جدید
- providers/image/base.py — BaseImageProvider abstract class
- providers/image/unsplash.py — UnsplashProvider (search + download)
- providers/image/pexels.py — PexelsProvider (search + download)
- providers/image/mock_image.py — MockImageProvider (PNG با stdlib)
- core/image_fill.py — query generation, file-type detection, temp → Media
- core/autofill.py — بروزرسانی: _fetch_all() حالا 3-tuple برمی‌گرداند
- config.json — اضافه شدن: image_enabled, image_provider, image_api_key, image_field
- ui/settings_dialog.py — اضافه شدن تب Image با: enable checkbox, field name, provider, API key (show/hide)

**نکات فنی مهم:**
- Image Query بعد از Stage 1 اجرا می‌شود تا بتواند از ترجمه انگلیسی استفاده کند
- نوع فایل تصویر از magic bytes تشخیص داده می‌شود (JPEG/PNG/GIF/WebP)
- نام فایل: autofill_img_{safe_word}.{ext} (مثال: autofill_img_mucho_gusto.jpg)
- فایل اول در tempfile.gettempdir() نوشته می‌شود، سپس با mw.col.media.add_file() به Media اضافه می‌شود
- تگ نهایی در فیلد: <img src="autofill_img_dog.jpg">

### نحوه تست:
1. در Settings → Image: Provider را روی mock بگذار
2. نام فیلد تصویر را وارد کنید (Image)
3. Auto Fill را بزنید — یک PNG آبی به عنوان placeholder ظاهر می‌شود
4. برای تصویر واقعی، Provider را عوض unsplash یا pexels بگذارید و API Key اضافه کنید

مثال:
- perro عکس سگ
- mucho gusto دو نفر که با هم آشنا می‌شوند

### چه باید پیاده‌سازی شود:
1. Image Query Generator — یک Image Query مناسب (به انگلیسی) از روی کلمه تولید کند
2. BaseImageProvider — abstract class در providers/image/base.py
3. Unsplash Provider یا Pexels Provider — جستجو و دانلود تصویر
4. ذخیره تصویر در Anki Media Collection با نام منحصربه‌فرد
5. قرار دادن تگ <img> در فیلد Image کارت
6. Image Provider قابل تنظیم از Settings

### فایل‌هایی که باید ساخته شوند:
```
providers/image/
├── __init__.py
├── base.py              <- BaseImageProvider
├── unsplash.py          <- Unsplash API provider
└── pexels.py            <- Pexels API provider (جایگزین)

core/
└── image_fill.py        <- منطق اصلی Image Fill
```

### نکات فنی مهم:
- Unsplash API رایگان دارد (نیاز به Access Key)
- Pexels API هم رایگان است
- تصویر باید با نام منحصربه‌فرد (hash یا UUID) در Media ذخیره شود
- باید در همان background thread انجام شود (نه در UI thread)
- برای ذخیره در Anki Media از mw.col.media.add_file(path) استفاده کن

---

## مرحله ۳ — Audio — COMPLETED

### وضعیت: تکمیل شده و قابل اجرا

### چه چیزی پیاده‌سازی شده:

**کارکرد اصلی:**
- در همان لحظه که Auto Fill زده می‌شود، صدای تلفظ کلمه هم به‌صورت خودکار دانلود می‌شود
- فایل MP3 در Anki Media Collection ذخیره می‌شود
- فیلد Audio کارت با تگ صوتی [sound:filename.mp3] پر می‌شود
- اگر دانلود صدا fail شود، خطا فقط log می‌شود و Auto Fill مرحله ۱ به کار خود ادامه می‌دهد (non-fatal)

**Audio Providers:**
- mock — فایل MP3 ساکت برای تست (بدون شبکه)
- gtts — Google Translate TTS endpoint (رایگان، بدون API Key، از urllib)

**فایل‌های ایجاد/بروزرسانی‌شده:**
- providers/audio/__init__.py — پکیج جدید
- providers/audio/base.py — BaseAudioProvider abstract class
- providers/audio/gtts_provider.py — GTTSProvider
- providers/audio/mock_audio.py — MockAudioProvider
- core/audio_fill.py — منطق اصلی: تبدیل نام زبان به BCP-47، دانلود، ذخیره در temp، افزودن به Anki Media
- core/autofill.py — بروزرسانی: _fetch_all() هم language data و هم audio را در یک background op دریافت می‌کند
- config.json — اضافه شدن audio_enabled, audio_provider, audio_field
- ui/settings_dialog.py — اضافه شدن تب Audio با: enable checkbox, field name, provider selector

**نکات فنی مهم:**
- URL: https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl={lang}&client=tw-ob
- نام فایل: autofill_{lang_code}_{safe_word}.mp3 (مثال: autofill_es_mucho_gusto.mp3)
- فایل اول در tempfile.gettempdir() ذخیره می‌شود، سپس با mw.col.media.add_file() به Media اضافه می‌شود
- LANG_TO_CODE map در core/audio_fill.py قرار دارد (28 زبان پشتیبانی می‌شود)

**نقشه زبان‌ها (LANG_TO_CODE):**
Spanish=es, French=fr, German=de, Italian=it, Portuguese=pt, Japanese=ja, Korean=ko, Chinese=zh-CN, Arabic=ar, Turkish=tr, Persian=fa, English=en, Russian=ru, Dutch=nl, Polish=pl ...

### نحوه تست:
1. در Settings → Audio: Provider را روی mock بگذار (برای تست بدون شبکه)
2. یا Provider را روی gtts بگذار (نیاز به اینترنت)
3. نام فیلد Audio را در Settings → Audio → Audio field name وارد کن
4. Auto Fill را بزن — هم اطلاعات زبانی و هم صدا پر می‌شوند

---

## مرحله ۲ — تصویر خودکار — NOT STARTED

### هدف:
تلفظ صوتی کلمه/عبارت را دریافت کرده و در Anki Media ذخیره کن.

مثال:
- mucho gusto فایل صوتی تلفظ اسپانیایی

### چه باید پیاده‌سازی شود:
1. BaseAudioProvider — abstract class
2. gTTS Provider — Google Text-to-Speech (رایگان، بدون API Key)
3. ذخیره فایل صوتی در Anki Media با فرمت [sound:filename.mp3]
4. قرار دادن tag صوتی در فیلد Audio

### فایل‌هایی که باید ساخته شوند:
```
providers/audio/
├── __init__.py
├── base.py              <- BaseAudioProvider
└── gtts_provider.py     <- gTTS provider
```

### نکات فنی:
- گزینه اصلی: استفاده از Google Translate TTS endpoint از طریق urllib (unofficial ولی رایگان)
  URL: https://translate.google.com/translate_tts?ie=UTF-8&tl=es&client=tw-ob&q=mucho+gusto
- فرمت نهایی در فیلد: [sound:mucho_gusto_es.mp3]
- فایل را به یک پوشه temp ذخیره کن، سپس با mw.col.media.add_file اضافه کن

---

## مرحله ۴ — امکانات نهایی — COMPLETED

### وضعیت: تکمیل شده و قابل اجرا

### چه چیزی پیاده‌سازی شده:

**۱. Preview Dialog قبل از ذخیره:**
- بعد از Auto Fill، یک پنجره Preview باز می‌شود
- کاربر همه فیلدهای دریافتی را می‌بیند
- دکمه −1 Apply: فیلدها را در Note می‌نویسد
- دکمه × Cancel: هیچ تغییری ایجاد نمی‌شود
- دکمه 🔄 Regenerate Image: بدون بستن Preview، عکس جدید دریافت می‌کند
- تصویر به‌صورت live در Preview نمایش داده می‌شود

**۲. کش Session (Cache):**
- اگر یک کلمه قبلاً جستجو شده، نتیجه از کش برگشت می‌شود (API صدا نمی‌شود)
- کش در پایان Session پاک می‌شود (Restart Anki = کش خالی)
- دکمه Clear Cache در Settings → General
- تعداد ارایه‌های Cache در Settings نمایش داده می‌شود

**۳. Settings → General تکمیل شد:**
- Behavior: توچ «نمایش Preview قبل از اعمال»
- Session Cache: لیبل تعداد ارایه + دکمه Clear Cache

**فایل‌های ایجاد/بروزرسانی‌شده:**
- core/cache.py — مودول کش با get(), put(), clear(), size()
- ui/preview_dialog.py — PreviewDialog با نمایش فیلد‌ها، تصویر، صدا، دکمه‌های Apply/Cancel/Regenerate
- core/autofill.py — بروزرسانی: Cache در _fetch_all، توابع _apply_to_note جدید، نمایش Preview Dialog
- config.json — اضافه preview_enabled
- ui/settings_dialog.py — Behavior و Cache sections در تب General

**نکات فنی مهم:**
- اگر preview_enabled=False در config باشد، داده‌ها مستقیماً بدون Preview اعمال می‌شوند
- تصویر با لود QPixmap از پوشه Media نمایش داده می‌شود
- Regenerate با QueryOp جدید در background اجرا می‌شود (پنجره بسته نمی‌شود)
- Cache کلید بلاد: word.lower()|source_lang|target_lang
- فقط نتیجه‌های موفق (lang_data != None) کش می‌شوند

### نحوه استفاده:
1. کلمه وارد کنید و Auto Fill بزنید
2. Preview باز می‌شود — همه داده‌ها را می‌بینید
3. کلیک «✓ Apply to Note» — خلاص!
4. اگر عکس خوب نبود: Regenerate Image را بزنید
5. دوباره همان کلمه را بزنید — از کش برمی‌گردد (بدون API call جدید)

### هدف: پولیش کامل add-on با تمام ویژگی‌های حرفه‌ای

### امکاناتی که باید اضافه شوند:
- Preview Dialog — قبل از ذخیره، یک پنجره نمایش داده شود
- Apply / Cancel — کاربر تأیید یا رد کند
- Regenerate Image — دکمه برای تولید مجدد تصویر
- Cache — نتایج API در حافظه cache شوند
- جلوگیری از Overwrite — قابل تنظیم
- مدیریت خطا — پیام‌های خطای واضح
- Logging — بدون ذخیره API Key
- Mock Mode — تست بدون API (قبلاً تا حدودی پیاده‌سازی شده)

### Workflow نهایی که باید پیاده‌سازی شود:
```
کاربر: "mucho gusto"
    ↓
[Auto Fill]
    ↓ (در background)
اطلاعات زبان پر می‌شود (مرحله ۱)
    ↓
تصویر مرتبط پیدا می‌شود (مرحله ۲)
    ↓
Audio دریافت می‌شود (مرحله ۳)
    ↓
Preview نمایش داده می‌شود (مرحله ۴)
    ↓
کاربر [Apply] را می‌زند
    ↓
کارت Anki کامل می‌شود
```

---

## الزامات فنی (برای تمام مراحل)

- Python — با Python bundled شده در Anki کار کند
- Anki Add-on API فعلی — از APIهای منسوخ استفاده نشود
- PyQt — فقط از طریق abstraction‌های Anki (aqt.qt)
- ساختار modular — هر بخش جداگانه و قابل تست
- Provider Architecture — برای Language / Image / Audio
- API Keyها در Settings — هرگز hard-code نشوند
- کد کامل و قابل اجرا — نه pseudocode

---

## یادداشت‌های مهم برای هوش مصنوعی بعدی

1. Package name: نام package از __name__.split(".")[0] به‌دست می‌آید.
   مثال: اگر پوشه اسمش "anki_language_autofill" باشد، package همان است.

2. Config management: از mw.addonManager.getConfig(package) و mw.addonManager.writeConfig(package, cfg) استفاده می‌شود.

3. Background operations: از aqt.operations.QueryOp با .run_in_background() استفاده شده.
   این روش صحیح در Anki جدید است. از threading.Thread استفاده نکن.

4. PyQt imports: همیشه از aqt.qt ایمپورت شوند، نه مستقیم از PyQt5 یا PyQt6.
   مثال: from aqt.qt import QDialog, QVBoxLayout

5. Media collection: برای ذخیره فایل در Anki Media:
   - از mw.col.media.add_file(absolute_path) استفاده کن
   - فایل اول در یک مسیر temp ذخیره می‌شود، سپس به media اضافه می‌شود

6. Hook system: از aqt.gui_hooks استفاده شود.
   مثال: editor_did_init_buttons.append(add_autofill_button)

7. مرحله ۱ کاملاً پیاده‌سازی شده است. قبل از شروع مرحله ۲، مطمئن شوید که مرحله ۱ روی Anki نصب و تست شده.

---

## تاریخچه تغییرات

| تاریخ | مرحله | توضیح |
|-------|-------|-------|
| 2026-08-14 | مرحله ۱ | پیاده‌سازی کامل Auto Fill با Mock/Gemini/OpenRouter providers، Settings Dialog با سه تب، Editor Button، Logging. تمام فیلدها: Translation, English, Pronunciation, Part of Speech, Gender, Example, Example Translation, CEFR, Notes. قابلیت: بدون overwrite فیلدهای پر، بدون خطا برای فیلدهای ناموجود، UI بدون freeze. |
| 2026-08-14 | مرحله ۳ | پیاده‌سازی Audio با GTTSProvider (Google Translate TTS - رایگان، بدون API Key). فایل‌های جدید: providers/audio/ (base, gtts, mock), core/audio_fill.py. بروزرسانی: autofill.py برای ادغام audio در همان background op, config.json, settings_dialog.py با تب Audio جدید. Audio failure غیر مهلک است و مرحله ۱ را متوقف نمی‌کند. |
| 2026-08-14 | مرحله ۲ | پیاده‌سازی Image با UnsplashProvider و PexelsProvider (هر دو رایگان). MockImageProvider خود PNG آبی با stdlib می‌سازد (بدون PIL). سیستم هوشمند Image Query بر اساس نوع کلمه (Noun/Verb/Phrase). فایل‌های جدید: providers/image/, core/image_fill.py. بروزرسانی: autofill.py (3-tuple), config.json, settings_dialog.py با تب Image جدید. Image failure هم غیر مهلک است. |
| 2026-08-14 | مرحله ۴ | اضافه Preview Dialog با Apply/Cancel/Regenerate Image. اضافه کش Session (cache.py) با get/put/clear/size. فایل‌های جدید: core/cache.py، ui/preview_dialog.py. بروزرسانی: autofill.py برای Preview + Cache، _apply_to_note جدید. Settings → General: Behavior + Cache sections. config.json: preview_enabled اضافه شد. پروژه به پایان رسید. |
| 2026-08-14 | تکمیل نهایی | حذف زبان‌های hardcode از mock.py (حالا زبان‌agnostic). ساخت خودکار Note Type در __init__.py با ۱۲ فیلد و قالب کارت dark-theme. حذف پوشه card_templates (اضافی). ساخت راهنمای کامل انگلیسی (README.md) و فارسی (GUIDE_FA.md) شامل دریافت API از Gemini، OpenRouter، Unsplash، Pexels. بروزرسانی config.md. پروژه ۱۰۰٪ کامل. |

---

## ✅ پروژه 100% تکمیل شد

همه چهار مرحله اجرا شد. Add-on آماده نصب و استفاده است.
