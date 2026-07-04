"""
Appify Store Bot - Keyboard Builders (v2.0 PREMIUM)
====================================================
Reply and Inline keyboard factories for the Telegram bot UI.
Premium design with numbered items, back buttons everywhere,
and multi-payment support (Stars / TON / PayPal).
"""

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import PRODUCT_CATALOG, CHANNEL_LINK, BOT_USERNAME, calculate_final_price


# ─── Reply Keyboards (Main Menu) ──────────────────────────────────────────────

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build the persistent main menu - premium layout."""
    builder = ReplyKeyboardBuilder()

    # Row 1: Products (main CTA)
    builder.row(
        KeyboardButton(text="🛒 المنتجات"),
        KeyboardButton(text="📋 قائمة الأسعار"),
    )
    # Row 2: Info + Rules
    builder.row(
        KeyboardButton(text="ℹ️ معلومات"),
        KeyboardButton(text="📝 القوانين"),
    )
    # Row 3: Profile + Support
    builder.row(
        KeyboardButton(text="👤 حسابي"),
        KeyboardButton(text="🛠 الدعم الفني"),
    )

    return builder.as_markup(resize_keyboard=True, persistent=True)


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Admin extended menu with management buttons."""
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="📊 الإحصائيات"),
        KeyboardButton(text="👥 المستخدمين"),
    )
    builder.row(
        KeyboardButton(text="📦 إدارة الطلبات"),
        KeyboardButton(text="⚙️ إعدادات المتجر"),
    )
    builder.row(
        KeyboardButton(text="📢 إشعار عام"),
        KeyboardButton(text="🚫 حظر مستخدم"),
    )
    builder.row(
        KeyboardButton(text="🔙 القائمة الرئيسية"),
    )

    return builder.as_markup(resize_keyboard=True, persistent=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Cancel/Back keyboard for dialogs."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ إلغاء"))
    return builder.as_markup(resize_keyboard=True)


# ─── Inline Keyboards ─────────────────────────────────────────────────────────

def get_categories_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for product categories - numbered premium style."""
    builder = InlineKeyboardBuilder()

    numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i, (cat_key, category) in enumerate(PRODUCT_CATALOG.items()):
        num = numbers[i] if i < len(numbers) else f"{i+1}."
        builder.button(
            text=f"{num} {category['emoji']} {category['name_ar']}",
            callback_data=f"category:{cat_key}"
        )

    builder.button(
        text="🔙 رجوع للقائمة",
        callback_data="menu:main"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_products_inline_keyboard(category_key: str, page: int = 0) -> InlineKeyboardMarkup:
    """Inline keyboard for products in a category - numbered with pagination."""
    builder = InlineKeyboardBuilder()
    category = PRODUCT_CATALOG.get(category_key)

    if category:
        items = list(category["items"].items())
        page_size = 8
        start = page * page_size
        end = start + page_size
        page_items = items[start:end]

        numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]

        for i, (prod_key, product) in enumerate(page_items):
            final_price = calculate_final_price(product["base_price_rub"])
            num = numbers[i] if i < len(numbers) else f"{i+1}."
            builder.button(
                text=f"{num} {product['name']} — {final_price}$",
                callback_data=f"product:{prod_key}"
            )

        # Pagination buttons
        total_pages = (len(items) + page_size - 1) // page_size
        if total_pages > 1:
            nav_row = []
            if page > 0:
                nav_row.append(InlineKeyboardButton(
                    text="◀️ السابق",
                    callback_data=f"products_page:{category_key}:{page-1}"
                ))
            nav_row.append(InlineKeyboardButton(
                text=f"📄 {page+1}/{total_pages}",
                callback_data="noop"
            ))
            if page < total_pages - 1:
                nav_row.append(InlineKeyboardButton(
                    text="التالي ▶️",
                    callback_data=f"products_page:{category_key}:{page+1}"
                ))
            builder.row(*nav_row)

    builder.button(
        text="🔙 رجوع للأقسام",
        callback_data="menu:categories"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_product_detail_keyboard(product_key: str, category_key: str) -> InlineKeyboardMarkup:
    """Inline keyboard for product detail - premium with buy button."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🛒 شراء الآن ✨",
        callback_data=f"buy:{product_key}"
    )
    builder.button(
        text="📤 مشاركة للقناة",
        callback_data=f"share_channel:{product_key}"
    )
    builder.button(
        text="🔙 رجوع للمنتجات",
        callback_data=f"category:{category_key}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_payment_method_keyboard(order_id: str, product_key: str) -> InlineKeyboardMarkup:
    """Payment method selection keyboard - Stars / TON / PayPal."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⭐ دفع بـ Telegram Stars",
        callback_data=f"pay:stars:{order_id}"
    )
    builder.button(
        text="💎 دفع بـ TON Keeper",
        callback_data=f"pay:ton:{order_id}"
    )
    builder.button(
        text="💵 دفع بـ PayPal",
        callback_data=f"pay:paypal:{order_id}"
    )
    builder.button(
        text="❌ إلغاء الطلب",
        callback_data=f"payment:cancel:{order_id}"
    )
    builder.button(
        text="🔙 رجوع للمنتج",
        callback_data=f"product:{product_key}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_stars_payment_keyboard(order_id: str, stars_amount: int) -> InlineKeyboardMarkup:
    """Telegram Stars payment keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"⭐ ادفع {stars_amount} نجمة",
        callback_data=f"pay:stars:confirm:{order_id}"
    )
    builder.button(
        text="🔙 رجوع لطرق الدفع",
        callback_data=f"pay:back:{order_id}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_ton_payment_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """TON payment keyboard with confirm button."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ أرسلت المبلغ - تأكيد الدفع",
        callback_data=f"pay:ton:confirm:{order_id}"
    )
    builder.button(
        text="🔙 رجوع لطرق الدفع",
        callback_data=f"pay:back:{order_id}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_paypal_payment_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """PayPal payment keyboard."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ أرسلت المبلغ - تأكيد الدفع",
        callback_data=f"pay:paypal:confirm:{order_id}"
    )
    builder.button(
        text="🔙 رجوع لطرق الدفع",
        callback_data=f"pay:back:{order_id}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_payment_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Legacy payment keyboard - kept for compatibility."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ تأكيد الدفع",
        callback_data=f"payment:confirm:{order_id}"
    )
    builder.button(
        text="❌ إلغاء الطلب",
        callback_data=f"payment:cancel:{order_id}"
    )
    builder.adjust(2)
    return builder.as_markup()


def get_profile_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard for user profile section."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📜 سجل الطلبات",
        callback_data=f"profile:orders:{user_id}"
    )
    builder.button(
        text="🎁 نظام الإحالة",
        callback_data=f"profile:referral:{user_id}"
    )
    builder.button(
        text="💰 شحن الرصيد",
        callback_data=f"profile:deposit:{user_id}"
    )
    builder.button(
        text="🔙 رجوع للقائمة",
        callback_data="menu:main"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_order_history_keyboard(telegram_id: int, page: int = 0, total: int = 0) -> InlineKeyboardMarkup:
    """Inline keyboard for order history with pagination."""
    builder = InlineKeyboardBuilder()

    page_size = 5
    total_pages = max(1, (total + page_size - 1) // page_size)

    if total_pages > 1:
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton(
                text="◀️ السابق",
                callback_data=f"orders_page:{telegram_id}:{page-1}"
            ))
        nav_row.append(InlineKeyboardButton(
            text=f"📄 {page+1}/{total_pages}",
            callback_data="noop"
        ))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(
                text="التالي ▶️",
                callback_data=f"orders_page:{telegram_id}:{page+1}"
            ))
        builder.row(*nav_row)

    builder.button(
        text="🔙 رجوع للحساب",
        callback_data=f"profile:main:{telegram_id}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_referral_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard for referral section."""
    builder = InlineKeyboardBuilder()

    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref{telegram_id}"

    builder.button(
        text="🔗 مشاركة رابط الإحالة",
        url=f"https://t.me/share/url?url={referral_link}&text=🌟%20انضم%20إلى%20متجر%20Appify%20Store%20وادفع%20بـ%20Stars%20أو%20TON!"
    )
    builder.button(
        text="🔙 رجوع للحساب",
        callback_data=f"profile:main:{telegram_id}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_support_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for support section."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📩 مراسلة الدعم",
        url=f"https://t.me/{BOT_USERNAME}"
    )
    builder.button(
        text="📢 قناتنا الرسمية",
        url=CHANNEL_LINK
    )
    builder.button(
        text="🔙 رجوع للقائمة",
        callback_data="menu:main"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_channel_post_keyboard(product_key: str) -> InlineKeyboardMarkup:
    """Inline keyboard for channel post with deep link."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🛒 شراء الآن",
        url=f"https://t.me/{BOT_USERNAME}?start=buy_{product_key}"
    )
    builder.button(
        text="📢 قناة المتجر",
        url=CHANNEL_LINK
    )
    builder.adjust(2)
    return builder.as_markup()


def get_admin_actions_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
    """Admin actions keyboard for user management."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🚫 حظر",
        callback_data=f"admin:ban:{target_user_id}"
    )
    builder.button(
        text="✅ فك الحظر",
        callback_data=f"admin:unban:{target_user_id}"
    )
    builder.button(
        text="📜 طلباته",
        callback_data=f"admin:orders:{target_user_id}"
    )
    builder.button(
        text="🔙 رجوع",
        callback_data="admin:users"
    )
    builder.adjust(3, 1)
    return builder.as_markup()


def get_order_action_keyboard(order_id: str, user_id: int) -> InlineKeyboardMarkup:
    """Admin order action keyboard - with deliver and refund."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ توصيل وإرسال للعميل",
        callback_data=f"order:deliver:{order_id}"
    )
    builder.button(
        text="❌ رفض واسترداد",
        callback_data=f"order:refund:{order_id}"
    )
    builder.button(
        text="👤 عرض بيانات العميل",
        callback_data=f"admin:view_user:{user_id}"
    )
    builder.button(
        text="🔙 رجوع للطلبات",
        callback_data="admin:orders"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_admin_pending_orders_keyboard(orders: list) -> InlineKeyboardMarkup:
    """Keyboard showing pending orders for quick admin action."""
    builder = InlineKeyboardBuilder()

    for order in orders[:10]:
        product_name = order.product.name if order.product else "؟"
        builder.button(
            text=f"📦 #{order.order_id[:8]} | {product_name[:20]}",
            callback_data=f"admin:order_detail:{order.order_id}"
        )

    builder.button(
        text="🔙 رجوع للوحة الإدارة",
        callback_data="admin:panel"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_delivery_confirm_keyboard(order_id: str) -> InlineKeyboardMarkup:
    """Keyboard for admin to confirm delivery details."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ إرسال للعميل الآن",
        callback_data=f"order:send_delivery:{order_id}"
    )
    builder.button(
        text="✏️ تعديل البيانات",
        callback_data=f"order:edit_delivery:{order_id}"
    )
    builder.button(
        text="🔙 رجوع",
        callback_data=f"admin:order_detail:{order_id}"
    )
    builder.adjust(1)
    return builder.as_markup()
