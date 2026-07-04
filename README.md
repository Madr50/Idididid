# 🍎 Appify Store Bot — v2.0 PREMIUM

بوت تيليغرام احترافي لبيع Apple IDs والألعاب بشكل مؤتمت مع دعم طرق دفع متعددة.

---

## ✨ المميزات الرئيسية

**المنتجات والواجهة:**
- صور مخصصة لكل لعبة وتطبيق تُحمَّل تلقائياً من الإنترنت
- أزرار مرقمة احترافية (1️⃣ 2️⃣ 3️⃣) مع زر رجوع في كل صفحة
- عرض تفصيلي لكل منتج مع الصورة والسعر والوصف
- تصفح بالأقسام مع pagination للمنتجات الكثيرة

**نظام الدفع المتعدد:**
- ⭐ **Telegram Stars** — دفع فوري عبر فاتورة تيليغرام الرسمية
- 💎 **TON Keeper** — تحويل TON مع تأكيد يدوي من الأدمن
- 💵 **PayPal** — تحويل Friends & Family مع تأكيد يدوي

**التسليم المؤتمت:**
- الأدمن يتلقى إشعاراً فورياً عند كل دفع
- من لوحة الإدارة: الأدمن يدخل Apple ID + كلمة المرور
- البوت يرسل البيانات للعميل تلقائياً مع تعليمات الاستخدام

**لوحة الإدارة:**
- إحصائيات شاملة (مستخدمون، طلبات، إيرادات)
- إدارة الطلبات المعلقة مع أزرار توصيل/رفض
- إذاعة رسائل لجميع المستخدمين
- حظر/فك حظر المستخدمين

---

## 🚀 التشغيل

### متغيرات البيئة المطلوبة

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
TON_WALLET_ADDRESS=your_ton_wallet
PAYPAL_EMAIL=your@paypal.com
PAYPAL_ME_LINK=https://paypal.me/yourname
```

### متغيرات اختيارية

```env
BOT_USERNAME=AppifyStore_bot
BOT_NAME=Appify Store | متجر آبيفاي
CHANNEL_USERNAME=AppifyStore0
PROFIT_MARGIN_PERCENT=25
EXCHANGE_RATE_RUB_TO_USD=0.011
STARS_RATE=0.013
TON_RATE_USD=5.5
```

### التثبيت والتشغيل

```bash
pip install -r requirements.txt
python main.py
```

---

## 📁 هيكل المشروع

```
bot_project/
├── main.py                    # نقطة الدخول الرئيسية
├── config.py                  # الإعدادات وكتالوج المنتجات
├── database.py                # قاعدة البيانات (SQLAlchemy + SQLite)
├── server.py                  # خادم Flask للـ keep-alive
├── requirements.txt           # التبعيات
├── frontend/
│   ├── handlers.py            # معالجات الرسائل والـ callbacks
│   └── keyboards.py           # مصانع الأزرار
├── backend/
│   └── sourcebot_bridge.py    # جسر Pyrogram (اختياري)
└── utils/
    └── image_watermark.py     # معالجة الصور وإضافة العلامة التجارية
```

---

## 💳 تدفق الشراء

```
المستخدم يختار منتج
        ↓
يضغط "شراء الآن"
        ↓
يختار طريقة الدفع (Stars / TON / PayPal)
        ↓
يتم إنشاء الطلب في قاعدة البيانات
        ↓
الأدمن يتلقى إشعاراً فورياً
        ↓
الأدمن يضغط "توصيل" ويدخل Apple ID + كلمة المرور
        ↓
البوت يرسل البيانات للعميل تلقائياً ✅
```

---

## 🛒 المنتجات المتاحة (21 منتج)

| القسم | المنتجات |
|-------|---------|
| 🎮 الألعاب | Minecraft, Terraria, Geometry Dash, GTA SA, Red Dead, Subnautica, Dead Cells, Tomb Raider, FNAF, ألعاب نادرة |
| 📱 التطبيقات | LumaFusion, FL Studio, Procreate, Procreate Dreams, Nomad Sculpt, Things 3, AnkiMobile |
| 🍎 Apple IDs | أمريكا 🇺🇸, تركيا 🇹🇷, روسيا 🇷🇺, مع Minecraft |

---

## 📞 الدعم الفني

الدعم الفني يكون عبر القناة الرسمية فقط.
