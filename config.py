"""
Appify Store Bot - Configuration Module (v2.0 PREMIUM)
======================================================
Secure environment-based configuration for the dropshipping bot.
All sensitive values are loaded from environment variables.
"""

import os
from pathlib import Path

# ─── Base Paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "data" / "appify.db"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for dir_path in [DATABASE_PATH.parent, ASSETS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ─── Bot Credentials ──────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8848866254:AAFUKRg-W8ZHKCW_KkYgRzcn4EIdaIsfxiU")
BOT_ID = int(os.getenv("BOT_ID", "8989271393"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "AppifyStore_bot")
BOT_NAME = os.getenv("BOT_NAME", "Appify Store | متجر آبيفاي")

# ─── Admin Configuration ──────────────────────────────────────────────────────
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

# ─── Telegram Channel ─────────────────────────────────────────────────────────
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "AppifyStore0")
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"

# ─── Pyrogram Userbot (SourceBot Automation) ──────────────────────────────────
PYROGRAM_API_ID = int(os.getenv("PYROGRAM_API_ID", "0"))
PYROGRAM_API_HASH = os.getenv("PYROGRAM_API_HASH", "")
PYROGRAM_SESSION_STRING = os.getenv("PYROGRAM_SESSION_STRING", "")
SOURCE_BOT_USERNAME = os.getenv("SOURCE_BOT_USERNAME", "SourceBot")

# ─── Payment Configuration ────────────────────────────────────────────────────
# Telegram Stars (1 Star ≈ 0.013 USD)
STARS_RATE = float(os.getenv("STARS_RATE", "0.013"))

# TON Keeper
TON_WALLET_ADDRESS = os.getenv("TON_WALLET_ADDRESS", "")  # Your TON wallet address
TON_RATE_USD = float(os.getenv("TON_RATE_USD", "5.5"))     # 1 TON = X USD

# PayPal
PAYPAL_EMAIL = os.getenv("PAYPAL_EMAIL", "")
PAYPAL_ME_LINK = os.getenv("PAYPAL_ME_LINK", "")

# ─── Pricing Configuration ────────────────────────────────────────────────────
PROFIT_MARGIN_PERCENT = float(os.getenv("PROFIT_MARGIN_PERCENT", "25"))
CURRENCY_DISPLAY = os.getenv("CURRENCY_DISPLAY", "USD")
EXCHANGE_RATE_RUB_TO_USD = float(os.getenv("EXCHANGE_RATE_RUB_TO_USD", "0.011"))

# ─── Flask Keep-Alive Server ──────────────────────────────────────────────────
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "8080"))

# ─── Bot Behavior ─────────────────────────────────────────────────────────────
ORDER_TIMEOUT_SECONDS = int(os.getenv("ORDER_TIMEOUT_SECONDS", "300"))
MAX_CONCURRENT_ORDERS = int(os.getenv("MAX_CONCURRENT_ORDERS", "10"))
PAYMENT_TIMEOUT_MINUTES = int(os.getenv("PAYMENT_TIMEOUT_MINUTES", "15"))

# ─── Referral System ──────────────────────────────────────────────────────────
REFERRAL_BONUS_PERCENT = float(os.getenv("REFERRAL_BONUS_PERCENT", "5"))

# ─── Watermark / Branding ─────────────────────────────────────────────────────
WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "Appify Store")
WATERMARK_OPACITY = int(os.getenv("WATERMARK_OPACITY", "80"))
BRAND_PRIMARY_COLOR = os.getenv("BRAND_PRIMARY_COLOR", "#0A0A1A")
BRAND_ACCENT_COLOR = os.getenv("BRAND_ACCENT_COLOR", "#E94560")
BRAND_SECONDARY_COLOR = os.getenv("BRAND_SECONDARY_COLOR", "#16213E")
BRAND_GOLD_COLOR = os.getenv("BRAND_GOLD_COLOR", "#FFD700")
BRAND_TEXT_COLOR = os.getenv("BRAND_TEXT_COLOR", "#FFFFFF")

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ─── Validate Critical Config ─────────────────────────────────────────────────
def validate_config():
    """Validate that all critical configuration values are set."""
    critical_vars = {
        "BOT_TOKEN": BOT_TOKEN,
        "PYROGRAM_API_ID": PYROGRAM_API_ID,
        "PYROGRAM_API_HASH": PYROGRAM_API_HASH,
        "PYROGRAM_SESSION_STRING": PYROGRAM_SESSION_STRING,
    }
    missing = [name for name, value in critical_vars.items() if not value or value == 0]
    if missing:
        print(f"[WARNING] Missing critical environment variables: {', '.join(missing)}")
        print("[INFO] Bot will start in limited mode without Pyrogram automation.")
    return len(missing) == 0


# ─── Product Catalog (v2.0 with Images & Descriptions) ───────────────────────
# image_url: direct image link for each product (game cover / app icon)
PRODUCT_CATALOG = {
    "games": {
        "emoji": "🎮",
        "name_ar": "الألعاب",
        "items": {
            "minecraft": {
                "name": "Minecraft",
                "name_ar": "ماين كرافت",
                "base_price_rub": 100,
                "description": "العبة الأسطورية! ابنِ عوالمك الخاصة وابدع بلا حدود.",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/5/51/Minecraft_cover.png",
            },
            "terraria": {
                "name": "Terraria",
                "name_ar": "تيراريا",
                "base_price_rub": 100,
                "description": "مغامرة ملحمية في عالم ثنائي الأبعاد مليء بالمخلوقات والكنوز.",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/1/1a/Terraria_Steam_artwork.jpg",
            },
            "geometry_dash": {
                "name": "Geometry Dash",
                "name_ar": "جيومتري داش",
                "base_price_rub": 100,
                "description": "لعبة إيقاع وتحديات مثيرة - اختبر ردود أفعالك!",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/a/a7/Geometry_Dash_Logo.PNG",
            },
            "gta_sa": {
                "name": "GTA: San Andreas",
                "name_ar": "جي تي ايه سان اندرياس",
                "base_price_rub": 100,
                "description": "الكلاسيكية الخالدة - عالم مفتوح لا ينتهي.",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/1/1a/GTA_San_Andreas_Box_Art.jpg",
            },
            "red_dead": {
                "name": "Red Dead Redemption",
                "name_ar": "ريد ديد ريدمبشن",
                "base_price_rub": 299,
                "description": "ملحمة الغرب الأمريكي - قصة لا تُنسى.",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/a/a7/Red_Dead_Redemption.jpg",
            },
            "subnautica": {
                "name": "Subnautica + Below Zero",
                "name_ar": "سبناوتيكا",
                "base_price_rub": 149,
                "description": "استكشف أعماق المحيطات الغامضة في عالم خيالي مذهل.",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/c/c9/Subnautica_cover_art.jpg",
            },
            "dead_cells": {
                "name": "Dead Cells",
                "name_ar": "ديد سيلز",
                "base_price_rub": 149,
                "description": "لعبة أكشن روغلايك - كل جولة تجربة جديدة!",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/3/36/Dead_Cells_cover_art.jpg",
            },
            "tomb_raider": {
                "name": "Tomb Raider",
                "name_ar": "تومب رايدر",
                "base_price_rub": 199,
                "description": "مغامرات لارا كروفت الأسطورية في أخطر الأماكن.",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/0/0e/Tomb_Raider_2013_cover.jpg",
            },
            "fnaf_all": {
                "name": "Five Nights at Freddy's",
                "name_ar": "فايف نايتس",
                "base_price_rub": 299,
                "description": "مجموعة ألعاب الرعب الأكثر شهرة في العالم!",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/c/c3/Five_Nights_at_Freddy%27s_cover.jpg",
            },
            "removed_games": {
                "name": "ألعاب محذوفة من المنطقة",
                "name_ar": "ألعاب نادرة",
                "base_price_rub": 100,
                "description": "ألعاب حصرية تم حذفها من المتاجر - احصل عليها الآن!",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg",
            },
        }
    },
    "apps": {
        "emoji": "📱",
        "name_ar": "التطبيقات",
        "items": {
            "lumafusion": {
                "name": "LumaFusion",
                "name_ar": "لوما فيوجن",
                "base_price_rub": 229,
                "description": "أقوى تطبيق مونتاج فيديو على الآيفون والآيباد.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/LumaFusion_icon.png/240px-LumaFusion_icon.png",
            },
            "fl_studio": {
                "name": "FL Studio Mobile",
                "name_ar": "اف ال ستوديو موبايل",
                "base_price_rub": 199,
                "description": "استوديو موسيقى كامل في جيبك - أنتج موسيقاك الآن.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/FL_Studio_v20.6_screenshot.png/320px-FL_Studio_v20.6_screenshot.png",
            },
            "procreate": {
                "name": "Procreate + Pocket",
                "name_ar": "بروكريت",
                "base_price_rub": 199,
                "description": "التطبيق الأول عالمياً للرسم الرقمي الاحترافي.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Procreate_logo.png/240px-Procreate_logo.png",
            },
            "procreate_dreams": {
                "name": "Procreate Dreams",
                "name_ar": "بروكريت دريمز",
                "base_price_rub": 199,
                "description": "تطبيق الأنيميشن الاحترافي من مطوري Procreate.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Procreate_logo.png/240px-Procreate_logo.png",
            },
            "nomad_sculpt": {
                "name": "Nomad Sculpt",
                "name_ar": "نوماد سكلبت",
                "base_price_rub": 199,
                "description": "نحت ثلاثي الأبعاد احترافي على هاتفك.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Nomad_Sculpt_icon.png/240px-Nomad_Sculpt_icon.png",
            },
            "things3": {
                "name": "Things 3",
                "name_ar": "ثينجز 3",
                "base_price_rub": 199,
                "description": "أفضل تطبيق لإدارة المهام والإنتاجية على iOS.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Things_3_icon.png/240px-Things_3_icon.png",
            },
            "anki": {
                "name": "AnkiMobile Flashcards",
                "name_ar": "أنكي موبايل",
                "base_price_rub": 229,
                "description": "تطبيق التعلم بالبطاقات الذكية - حفظ أسرع وأقوى.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Anki-icon.svg/240px-Anki-icon.svg.png",
            },
        }
    },
    "apple_ids": {
        "emoji": "🍎",
        "name_ar": "حسابات Apple ID",
        "items": {
            "id_usa": {
                "name": "Apple ID 🇺🇸 أمريكا",
                "name_ar": "آبل آيدي أمريكا",
                "base_price_rub": 299,
                "description": "حساب Apple ID أمريكي - وصول كامل لجميع التطبيقات الأمريكية.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/240px-Apple_logo_black.svg.png",
            },
            "id_turkey": {
                "name": "Apple ID 🇹🇷 تركيا",
                "name_ar": "آبل آيدي تركيا",
                "base_price_rub": 299,
                "description": "حساب Apple ID تركي - أسعار مخفضة وتطبيقات حصرية.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/240px-Apple_logo_black.svg.png",
            },
            "id_russia": {
                "name": "Apple ID 🇷🇺 روسيا",
                "name_ar": "آبل آيدي روسيا",
                "base_price_rub": 299,
                "description": "حساب Apple ID روسي - ألعاب وتطبيقات حصرية.",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/240px-Apple_logo_black.svg.png",
            },
            "id_minecraft": {
                "name": "Apple ID 🎮 مع Minecraft",
                "name_ar": "آبل آيدي مع ماينكرافت",
                "base_price_rub": 949,
                "description": "حساب Apple ID جاهز مع لعبة Minecraft مثبتة مسبقاً!",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/5/51/Minecraft_cover.png",
            },
        }
    }
}


def calculate_final_price(base_price_rub: int) -> float:
    """Calculate final price with profit margin."""
    base_in_currency = base_price_rub * EXCHANGE_RATE_RUB_TO_USD
    final_price = base_in_currency * (1 + PROFIT_MARGIN_PERCENT / 100)
    return round(final_price, 2)


def price_to_stars(usd_price: float) -> int:
    """Convert USD price to Telegram Stars."""
    stars = int(usd_price / STARS_RATE)
    return max(stars, 1)


def price_to_ton(usd_price: float) -> float:
    """Convert USD price to TON."""
    return round(usd_price / TON_RATE_USD, 4)


def get_all_products():
    """Get flat list of all products with calculated prices."""
    products = []
    for cat_key, category in PRODUCT_CATALOG.items():
        for prod_key, product in category["items"].items():
            products.append({
                "id": prod_key,
                "category": cat_key,
                "category_emoji": category["emoji"],
                "category_name_ar": category["name_ar"],
                "name": product["name"],
                "name_ar": product.get("name_ar", product["name"]),
                "description": product.get("description", ""),
                "base_price_rub": product["base_price_rub"],
                "final_price": calculate_final_price(product["base_price_rub"]),
                "image_url": product.get("image_url", ""),
            })
    return products


# ─── Arabic Text Templates (v2.0 PREMIUM) ────────────────────────────────────
class TextTemplates:
    """Centralized Arabic text templates for consistent messaging."""

    WELCOME_MESSAGE = """
🌟 **أهلاً وسهلاً في {bot_name}!**

╔══════════════════════════╗
║  🍎 **متجرك الموثوق**  ║
║  لـ Apple IDs والألعاب  ║
╚══════════════════════════╝

✨ **مميزاتنا:**
⚡ توصيل فوري ومؤتمت
🔒 حسابات موثوقة 100%
💎 أسعار لا تُنافَس
🛡️ ضمان كامل على جميع المنتجات

💳 **طرق الدفع المتاحة:**
⭐ Telegram Stars | 💎 TON | 💵 PayPal

━━━━━━━━━━━━━━━━━━━━━━━━
🔰 **اختر من القائمة أدناه للبدء:**
"""

    RULES_MESSAGE = """
📜 **قوانين وشروط الاستخدام**

━━━━━━━━━━━━━━━━━━━━━━━━

🚫 **ممنوع منعاً باتاً:**

`1.1` يمنع مشاركة أو إعادة بيع الحساب لأي طرف آخر
`1.2` يمنع تسجيل الدخول عبر iCloud أو الإعدادات
`1.3` يمنع تغيير أي بيانات (المنطقة، الاسم، الإيميل، كلمة المرور)
`1.4` يمنع الدخول لموقع Apple الرسمي - فقط App Store

━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **غير مستحسن:**

`2.1` لا تدخل الحساب بعد 24 ساعة من الشراء
`2.2` لا تدخل كلمة المرور خطأ أكثر من 3 مرات
`2.3` لا تحاول شراء ألعاب إضافية على الحساب
`2.4` لا تستخدمه كحسابك الأساسي
`2.5` لا تسجل الدخول في iTunes أو Apple TV

━━━━━━━━━━━━━━━━━━━━━━━━

⚖️ **عند المخالفة:**
يحق لنا رفض الخدمة وتقييد وصولك دون استرداد.
"""

    INFO_MESSAGE = """
ℹ️ **معلومات عن المتجر**

━━━━━━━━━━━━━━━━━━━━━━━━

🏪 **{bot_name}**
وجهتك الأولى لشراء Apple IDs والألعاب

━━━━━━━━━━━━━━━━━━━━━━━━

✅ **مميزاتنا:**
• ⚡ توصيل فوري مؤتمت
• 🔒 ضمان كامل على جميع المنتجات
• 💬 دعم فني متاح دائماً
• 💰 أسعار تنافسية
• 🎁 نظام إحالة مجزٍ

━━━━━━━━━━━━━━━━━━━━━━━━

💳 **طرق الدفع:**
⭐ Telegram Stars (أسرع طريقة)
💎 TON Keeper
💵 PayPal

━━━━━━━━━━━━━━━━━━━━━━━━

📢 **قناتنا:** {channel_link}
🤖 **البوت:** @{bot_username}
"""

    SUPPORT_MESSAGE = """
🛠️ **الدعم الفني**

━━━━━━━━━━━━━━━━━━━━━━━━

📩 **للتواصل مع فريق الدعم:**
• صف مشكلتك بالتفصيل
• أرفق لقطة شاشة إن أمكن
• سيتم الرد عليك في أقرب وقت

━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **قناة الدعم:** {channel_link}

💡 **ملاحظة:** الدعم الفني يكون عبر القناة الرسمية فقط
"""

    ORDER_CONFIRMATION = """
✅ **تم إنشاء طلبك بنجاح!**

━━━━━━━━━━━━━━━━━━━━━━━━

🆔 **رقم الطلب:** `{order_id}`
📦 **المنتج:** {product_name}
💰 **السعر:** {price} USD

━━━━━━━━━━━━━━━━━━━━━━━━

💳 **اختر طريقة الدفع:**
"""

    PAYMENT_STARS_INFO = """
⭐ **الدفع بـ Telegram Stars**

━━━━━━━━━━━━━━━━━━━━━━━━

🆔 **الطلب:** `{order_id}`
📦 **المنتج:** {product_name}
⭐ **المبلغ:** `{stars_amount}` نجمة

━━━━━━━━━━━━━━━━━━━━━━━━

💡 يمكنك شراء النجوم من داخل تيليغرام مباشرة
اضغط **ادفع الآن** لإتمام العملية
"""

    PAYMENT_TON_INFO = """
💎 **الدفع بـ TON Keeper**

━━━━━━━━━━━━━━━━━━━━━━━━

🆔 **الطلب:** `{order_id}`
📦 **المنتج:** {product_name}
💎 **المبلغ:** `{ton_amount}` TON

━━━━━━━━━━━━━━━━━━━━━━━━

📋 **عنوان المحفظة:**
`{ton_wallet}`

━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ أرسل المبلغ بالضبط ثم اضغط **تأكيد الدفع**
"""

    PAYMENT_PAYPAL_INFO = """
💵 **الدفع بـ PayPal**

━━━━━━━━━━━━━━━━━━━━━━━━

🆔 **الطلب:** `{order_id}`
📦 **المنتج:** {product_name}
💵 **المبلغ:** `{usd_amount}` USD

━━━━━━━━━━━━━━━━━━━━━━━━

📧 **PayPal:** `{paypal_email}`

━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ أرسل المبلغ كـ "Friends & Family" ثم اضغط **تأكيد الدفع**
"""

    DELIVERY_MESSAGE = """
🎉 **تم توصيل طلبك بنجاح!**

━━━━━━━━━━━━━━━━━━━━━━━━

📦 **المنتج:** {product_name}
🆔 **رقم الطلب:** `{order_id}`

━━━━━━━━━━━━━━━━━━━━━━━━

📧 **Apple ID:** `{apple_id}`
🔑 **كلمة المرور:** `{password}`

━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **تعليمات مهمة جداً:**
✅ سجل الدخول فقط عبر App Store
❌ لا تدخل عبر iCloud أو الإعدادات
❌ لا تغير أي بيانات في الحساب
📖 اقرأ القوانين كاملاً

🙏 شكراً لثقتك بنا - عودة قريبة!
"""

    PROFILE_TEMPLATE = """
👤 **حسابي**

━━━━━━━━━━━━━━━━━━━━━━━━

🆔 **المعرف:** `{user_id}`
👤 **الاسم:** {name}
📅 **تاريخ التسجيل:** {reg_date}

━━━━━━━━━━━━━━━━━━━━━━━━

📊 **إحصائياتي:**
🛒 عدد الطلبات: **{orders_count}**
💰 إجمالي المشتريات: **{total_spent} USD**
🎁 الإحالات: **{referrals_count}**

━━━━━━━━━━━━━━━━━━━━━━━━

💎 **العضوية:** {membership}
"""

    REFERRAL_MESSAGE = """
🎁 **نظام الإحالة**

━━━━━━━━━━━━━━━━━━━━━━━━

🔗 **رابط الإحالة الخاص بك:**
`{referral_link}`

━━━━━━━━━━━━━━━━━━━━━━━━

💰 **لكل صديق يشتري عبر رابطك:**
تحصل على **{bonus_percent}%** من قيمة مشترياته!

━━━━━━━━━━━━━━━━━━━━━━━━

📊 **إحصائياتك:**
👥 عدد الإحالات: **{referrals_count}**
💵 إجمالي الأرباح: **{total_earnings} USD**

📢 شارك الرابط وابدأ بالربح الآن!
"""

    ADMIN_STATS = """
📊 **لوحة الإحصائيات**

━━━━━━━━━━━━━━━━━━━━━━━━

👥 **إجمالي المستخدمين:** `{total_users}`
📦 **إجمالي الطلبات:** `{total_orders}`
💰 **إجمالي المبيعات:** `{total_revenue}` USD
📅 **طلبات اليوم:** `{today_orders}`

━━━━━━━━━━━━━━━━━━━━━━━━
"""

    PRICE_LIST_HEADER = "📋 **قائمة الأسعار الكاملة**\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    NO_ORDERS_MESSAGE = """
📭 **لا يوجد لديك طلبات حالياً.**

🛒 ابدأ التسوق الآن من قسم المنتجات!
"""

    ORDER_HISTORY_HEADER = "📜 **سجل طلباتك:**\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
