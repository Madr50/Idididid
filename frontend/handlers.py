"""
Appify Store Bot - Frontend Handlers (v2.0 PREMIUM)
====================================================
Aiogram 3.x message and callback handlers for the Telegram bot.
Features:
  - Multi-payment: Telegram Stars / TON / PayPal
  - Product images for every game/app
  - Professional numbered buttons with back navigation
  - Automated delivery on admin approval
  - Full admin panel with order management
"""

import datetime
import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (
    BOT_NAME, BOT_USERNAME, CHANNEL_LINK,
    TextTemplates, PRODUCT_CATALOG, calculate_final_price,
    ADMIN_IDS, price_to_stars, price_to_ton,
    TON_WALLET_ADDRESS, PAYPAL_EMAIL, PAYPAL_ME_LINK,
    BOT_TOKEN,
)
from database import (
    get_or_create_user, get_user, get_all_products_db,
    get_product_by_key, get_product_by_id,
    create_order, get_user_orders, get_order, deliver_order,
    get_full_stats, ban_user, unban_user,
    log_admin_action, update_order_status,
    get_recent_orders, get_pending_orders,
    set_order_payment_info, refund_order,
)
from frontend.keyboards import (
    get_main_menu_keyboard, get_admin_menu_keyboard, get_cancel_keyboard,
    get_categories_inline_keyboard, get_products_inline_keyboard,
    get_product_detail_keyboard, get_payment_method_keyboard,
    get_stars_payment_keyboard, get_ton_payment_keyboard,
    get_paypal_payment_keyboard, get_payment_keyboard,
    get_profile_inline_keyboard, get_order_history_keyboard,
    get_referral_keyboard, get_support_keyboard,
    get_channel_post_keyboard, get_admin_actions_keyboard,
    get_order_action_keyboard, get_admin_pending_orders_keyboard,
    get_delivery_confirm_keyboard,
)
from utils.image_watermark import process_product_image, generate_channel_post_image

router = Router()
logger = logging.getLogger("AppifyBot.handlers")


# ─── FSM States ───────────────────────────────────────────────────────────────

class BroadcastState(StatesGroup):
    waiting_message = State()


class SupportState(StatesGroup):
    waiting_message = State()


class DeliveryState(StatesGroup):
    waiting_apple_id = State()
    waiting_password = State()


class AdminActionState(StatesGroup):
    waiting_user_id = State()
    action = State()


# ─── Helper Functions ─────────────────────────────────────────────────────────

def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


def escape_markdown(text: str) -> str:
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars:
        text = text.replace(char, f'\\{char}')
    return text


async def send_product_with_image(
    target,
    product,
    caption: str,
    keyboard: InlineKeyboardMarkup,
    edit: bool = False,
):
    """Send product message with image if available, else text."""
    image_buffer = None

    if product.image_url:
        try:
            image_buffer = await process_product_image(
                image_source=product.image_url,
                product_name=product.name,
                category=f"{product.category_emoji} {product.category_name_ar}",
                price=str(product.final_price),
                currency="USD",
            )
        except Exception as e:
            logger.warning(f"Image generation failed for {product.product_key}: {e}")

    if image_buffer:
        if edit and hasattr(target, 'edit_media'):
            from aiogram.types import InputMediaPhoto
            try:
                await target.edit_media(
                    media=InputMediaPhoto(
                        media=image_buffer,
                        caption=caption,
                        parse_mode="Markdown",
                    ),
                    reply_markup=keyboard,
                )
                return
            except Exception:
                pass
        try:
            await target.answer_photo(
                photo=image_buffer,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
        except Exception:
            await target.answer(caption, parse_mode="Markdown", reply_markup=keyboard)
    else:
        if edit and hasattr(target, 'edit_text'):
            try:
                await target.edit_text(caption, parse_mode="Markdown", reply_markup=keyboard)
                return
            except Exception:
                pass
        await target.answer(caption, parse_mode="Markdown", reply_markup=keyboard)


# ─── Start & Main Menu ────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - register user and show welcome."""
    await state.clear()

    args = message.text.split()[1] if len(message.text.split()) > 1 else None
    referrer_id = None
    product_key = None

    if args:
        if args.startswith("ref"):
            try:
                referrer_id = int(args[3:])
            except ValueError:
                pass
        elif args.startswith("buy_"):
            product_key = args[4:]
        elif args.isdigit():
            referrer_id = int(args)

    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code or "ar",
        referrer_id=referrer_id,
    )

    if user.is_banned:
        await message.answer(
            "🚫 **تم حظرك من استخدام البوت.**\n\nللاستفسار، تواصل مع الإدارة.",
            parse_mode="Markdown"
        )
        return

    if product_key:
        product = await get_product_by_key(product_key)
        if product:
            await show_product_detail(message, product)
            return

    welcome_text = TextTemplates.WELCOME_MESSAGE.format(
        bot_name=BOT_NAME,
        channel_link=CHANNEL_LINK,
        bot_username=BOT_USERNAME,
    )

    keyboard = get_admin_menu_keyboard() if is_admin(message.from_user.id) else get_main_menu_keyboard()

    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@router.message(F.text == "🔙 القائمة الرئيسية")
@router.message(Command("menu"))
async def show_main_menu(message: Message, state: FSMContext):
    """Show main menu."""
    await state.clear()
    user = await get_user(message.from_user.id)

    if user and user.is_banned:
        await message.answer("🚫 تم حظرك من البوت.")
        return

    welcome_text = TextTemplates.WELCOME_MESSAGE.format(
        bot_name=BOT_NAME,
        channel_link=CHANNEL_LINK,
        bot_username=BOT_USERNAME,
    )

    keyboard = get_admin_menu_keyboard() if is_admin(message.from_user.id) else get_main_menu_keyboard()

    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# ─── Products Section ─────────────────────────────────────────────────────────

@router.message(F.text == "🛒 المنتجات")
async def show_categories(message: Message):
    """Show product categories with numbered buttons."""
    user = await get_user(message.from_user.id)
    if not user or user.is_banned:
        return

    await message.answer(
        "🛒 **اختر القسم:**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "لدينا ألعاب iOS، تطبيقات احترافية، وحسابات Apple ID جاهزة!",
        parse_mode="Markdown",
        reply_markup=get_categories_inline_keyboard(),
    )


@router.callback_query(F.data.startswith("category:"))
async def callback_category(callback: CallbackQuery):
    """Handle category selection - show numbered products."""
    category_key = callback.data.split(":")[1]
    category = PRODUCT_CATALOG.get(category_key)

    if not category:
        await callback.answer("❌ القسم غير موجود", show_alert=True)
        return

    products_kb = get_products_inline_keyboard(category_key)
    await callback.message.edit_text(
        f"{category['emoji']} **قسم {category['name_ar']}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"اختر المنتج لعرض التفاصيل والصورة:",
        parse_mode="Markdown",
        reply_markup=products_kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("products_page:"))
async def callback_products_page(callback: CallbackQuery):
    """Handle product list pagination."""
    parts = callback.data.split(":")
    category_key = parts[1]
    page = int(parts[2])

    category = PRODUCT_CATALOG.get(category_key)
    if not category:
        await callback.answer("❌ القسم غير موجود", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=get_products_inline_keyboard(category_key, page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product:"))
async def callback_product(callback: CallbackQuery):
    """Show product details with image."""
    product_key = callback.data.split(":")[1]
    product = await get_product_by_key(product_key)

    if not product:
        await callback.answer("❌ المنتج غير موجود", show_alert=True)
        return

    await show_product_detail(callback.message, product, edit=True)
    await callback.answer()


async def show_product_detail(message_or_callback, product, edit: bool = False):
    """Display product detail with image and purchase options."""
    final_price = product.final_price
    stars_amount = price_to_stars(final_price)
    ton_amount = price_to_ton(final_price)

    caption = (
        f"{product.category_emoji} **{product.name}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 **القسم:** {product.category_name_ar}\n"
        f"💰 **السعر:** `{final_price}` USD\n\n"
    )

    if product.description:
        caption += f"📝 **الوصف:** {product.description}\n\n"

    caption += (
        f"💳 **طرق الدفع:**\n"
        f"⭐ {stars_amount} نجمة | 💎 {ton_amount} TON | 💵 {final_price}$ PayPal\n\n"
        f"🛒 اضغط **شراء الآن** لإتمام الشراء"
    )

    keyboard = get_product_detail_keyboard(product.product_key, product.category)

    await send_product_with_image(
        target=message_or_callback,
        product=product,
        caption=caption,
        keyboard=keyboard,
        edit=edit,
    )


# ─── Purchase Flow ────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("buy:"))
async def callback_buy(callback: CallbackQuery):
    """Initiate purchase flow - show payment methods."""
    product_key = callback.data.split(":")[1]
    product = await get_product_by_key(product_key)

    if not product:
        await callback.answer("❌ المنتج غير متوفر", show_alert=True)
        return

    order = await create_order(
        telegram_id=callback.from_user.id,
        product_id=product.id,
        price_paid=product.final_price,
        currency="USD",
    )

    if not order:
        await callback.answer("❌ حدث خطأ في إنشاء الطلب، حاول مرة أخرى", show_alert=True)
        return

    confirm_text = TextTemplates.ORDER_CONFIRMATION.format(
        order_id=order.order_id,
        product_name=product.name,
        price=product.final_price,
        currency="USD",
        date=order.created_at.strftime("%Y-%m-%d %H:%M"),
    )

    try:
        await callback.message.edit_text(
            confirm_text,
            parse_mode="Markdown",
            reply_markup=get_payment_method_keyboard(order.order_id, product_key),
        )
    except Exception:
        await callback.message.answer(
            confirm_text,
            parse_mode="Markdown",
            reply_markup=get_payment_method_keyboard(order.order_id, product_key),
        )
    await callback.answer()


# ─── Stars Payment ────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("pay:stars:") & ~F.data.startswith("pay:stars:confirm:"))
async def callback_pay_stars(callback: CallbackQuery):
    """Show Telegram Stars payment info."""
    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    if order.user_id != callback.from_user.id:
        await callback.answer("❌ هذا الطلب ليس لك", show_alert=True)
        return

    stars_amount = price_to_stars(order.price_paid)
    product_name = order.product.name if order.product else "المنتج"

    await set_order_payment_info(order_id, "stars", stars_amount=stars_amount)

    text = TextTemplates.PAYMENT_STARS_INFO.format(
        order_id=order_id,
        product_name=product_name,
        stars_amount=stars_amount,
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_stars_payment_keyboard(order_id, stars_amount),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_stars_payment_keyboard(order_id, stars_amount),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:stars:confirm:"))
async def callback_pay_stars_confirm(callback: CallbackQuery, bot: Bot):
    """Process Stars payment via Telegram invoice."""
    order_id = callback.data.split(":")[3]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    stars_amount = price_to_stars(order.price_paid)
    product_name = order.product.name if order.product else "المنتج"

    try:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"🛒 {product_name}",
            description=f"شراء {product_name} من Appify Store",
            payload=f"order:{order_id}",
            currency="XTR",
            prices=[LabeledPrice(label=product_name, amount=stars_amount)],
        )
        await callback.answer("⭐ تم إرسال فاتورة الدفع!")
    except Exception as e:
        logger.error(f"Stars invoice error: {e}")
        await callback.answer(
            "⚠️ حدث خطأ في إنشاء فاتورة Stars. تواصل مع الدعم.",
            show_alert=True
        )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery, bot: Bot):
    """Handle pre-checkout query for Stars payment."""
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, bot: Bot):
    """Handle successful Stars payment."""
    payload = message.successful_payment.invoice_payload
    if payload.startswith("order:"):
        order_id = payload.split(":")[1]
        order = await get_order(order_id)

        if order:
            await update_order_status(order_id, "paid", payment_method="stars")

            await message.answer(
                f"⭐ **تم الدفع بنجاح!**\n\n"
                f"🆔 رقم الطلب: `{order_id}`\n"
                f"⏳ جاري معالجة طلبك...\n\n"
                f"سيتم إرسال بيانات الحساب فور قبول الطلب من الإدارة.",
                parse_mode="Markdown",
            )

            # Notify admins
            product_name = order.product.name if order.product else "؟"
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"⭐ **دفع Stars جديد!**\n\n"
                        f"🆔 الطلب: `{order_id}`\n"
                        f"👤 المستخدم: `{message.from_user.id}`\n"
                        f"📦 المنتج: {product_name}\n"
                        f"⭐ المبلغ: {message.successful_payment.total_amount} نجمة\n\n"
                        f"⚠️ **يرجى توصيل الطلب من لوحة الإدارة**",
                        parse_mode="Markdown",
                        reply_markup=get_order_action_keyboard(order_id, message.from_user.id),
                    )
                except Exception as e:
                    logger.warning(f"Could not notify admin {admin_id}: {e}")


# ─── TON Payment ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("pay:ton:") & ~F.data.startswith("pay:ton:confirm:"))
async def callback_pay_ton(callback: CallbackQuery):
    """Show TON payment info."""
    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    if order.user_id != callback.from_user.id:
        await callback.answer("❌ هذا الطلب ليس لك", show_alert=True)
        return

    ton_amount = price_to_ton(order.price_paid)
    product_name = order.product.name if order.product else "المنتج"
    wallet = TON_WALLET_ADDRESS or "⚠️ لم يتم إعداد محفظة TON بعد"

    await set_order_payment_info(order_id, "ton", ton_amount=ton_amount)

    text = TextTemplates.PAYMENT_TON_INFO.format(
        order_id=order_id,
        product_name=product_name,
        ton_amount=ton_amount,
        ton_wallet=wallet,
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_ton_payment_keyboard(order_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_ton_payment_keyboard(order_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:ton:confirm:"))
async def callback_pay_ton_confirm(callback: CallbackQuery, bot: Bot):
    """Handle TON payment confirmation (manual verification)."""
    order_id = callback.data.split(":")[3]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    await update_order_status(order_id, "paid", payment_method="ton")

    await callback.message.edit_text(
        f"💎 **تم تأكيد الدفع بـ TON!**\n\n"
        f"🆔 رقم الطلب: `{order_id}`\n"
        f"⏳ جاري التحقق من الدفع...\n\n"
        f"سيتم إرسال بيانات الحساب فور التأكيد من الإدارة.",
        parse_mode="Markdown",
    )

    product_name = order.product.name if order.product else "؟"
    ton_amount = order.ton_amount or price_to_ton(order.price_paid)

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"💎 **دفع TON جديد - يحتاج تحقق!**\n\n"
                f"🆔 الطلب: `{order_id}`\n"
                f"👤 المستخدم: `{callback.from_user.id}`\n"
                f"📦 المنتج: {product_name}\n"
                f"💎 المبلغ: {ton_amount} TON\n\n"
                f"⚠️ **تحقق من الدفع ثم وصّل الطلب**",
                parse_mode="Markdown",
                reply_markup=get_order_action_keyboard(order_id, callback.from_user.id),
            )
        except Exception as e:
            logger.warning(f"Could not notify admin {admin_id}: {e}")

    await callback.answer("✅ تم إرسال طلبك للمراجعة!")


# ─── PayPal Payment ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("pay:paypal:") & ~F.data.startswith("pay:paypal:confirm:"))
async def callback_pay_paypal(callback: CallbackQuery):
    """Show PayPal payment info."""
    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    if order.user_id != callback.from_user.id:
        await callback.answer("❌ هذا الطلب ليس لك", show_alert=True)
        return

    product_name = order.product.name if order.product else "المنتج"
    paypal_email = PAYPAL_EMAIL or "⚠️ لم يتم إعداد PayPal بعد"

    await set_order_payment_info(order_id, "paypal")

    text = TextTemplates.PAYMENT_PAYPAL_INFO.format(
        order_id=order_id,
        product_name=product_name,
        usd_amount=order.price_paid,
        paypal_email=paypal_email,
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_paypal_payment_keyboard(order_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_paypal_payment_keyboard(order_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:paypal:confirm:"))
async def callback_pay_paypal_confirm(callback: CallbackQuery, bot: Bot):
    """Handle PayPal payment confirmation."""
    order_id = callback.data.split(":")[3]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    await update_order_status(order_id, "paid", payment_method="paypal")

    await callback.message.edit_text(
        f"💵 **تم تأكيد الدفع بـ PayPal!**\n\n"
        f"🆔 رقم الطلب: `{order_id}`\n"
        f"⏳ جاري التحقق من الدفع...\n\n"
        f"سيتم إرسال بيانات الحساب فور التأكيد من الإدارة.",
        parse_mode="Markdown",
    )

    product_name = order.product.name if order.product else "؟"

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"💵 **دفع PayPal جديد - يحتاج تحقق!**\n\n"
                f"🆔 الطلب: `{order_id}`\n"
                f"👤 المستخدم: `{callback.from_user.id}`\n"
                f"📦 المنتج: {product_name}\n"
                f"💵 المبلغ: {order.price_paid} USD\n\n"
                f"⚠️ **تحقق من الدفع ثم وصّل الطلب**",
                parse_mode="Markdown",
                reply_markup=get_order_action_keyboard(order_id, callback.from_user.id),
            )
        except Exception as e:
            logger.warning(f"Could not notify admin {admin_id}: {e}")

    await callback.answer("✅ تم إرسال طلبك للمراجعة!")


# ─── Payment Back Button ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("pay:back:"))
async def callback_pay_back(callback: CallbackQuery):
    """Return to payment method selection."""
    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    product_name = order.product.name if order.product else "المنتج"
    product_key = order.product.product_key if order.product else ""

    confirm_text = TextTemplates.ORDER_CONFIRMATION.format(
        order_id=order_id,
        product_name=product_name,
        price=order.price_paid,
        currency="USD",
        date=order.created_at.strftime("%Y-%m-%d %H:%M"),
    )

    try:
        await callback.message.edit_text(
            confirm_text,
            parse_mode="Markdown",
            reply_markup=get_payment_method_keyboard(order_id, product_key),
        )
    except Exception:
        pass
    await callback.answer()


# ─── Cancel Order ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("payment:cancel:"))
async def callback_payment_cancel(callback: CallbackQuery):
    """Handle order cancellation."""
    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    if order.user_id != callback.from_user.id:
        await callback.answer("❌ هذا الطلب ليس لك", show_alert=True)
        return

    await update_order_status(order_id, "failed", error_message="Cancelled by user")

    try:
        await callback.message.edit_text(
            "❌ **تم إلغاء الطلب.**\n\n"
            "يمكنك إعادة المحاولة في أي وقت من قسم المنتجات.",
            parse_mode="Markdown",
            reply_markup=get_categories_inline_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            "❌ **تم إلغاء الطلب.**",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer()


# ─── Price List ───────────────────────────────────────────────────────────────

@router.message(F.text == "📋 قائمة الأسعار")
async def show_price_list(message: Message):
    """Show formatted price list."""
    user = await get_user(message.from_user.id)
    if not user or user.is_banned:
        return

    products = await get_all_products_db()

    text = TextTemplates.PRICE_LIST_HEADER
    current_category = ""

    for product in products:
        if product.category != current_category:
            current_category = product.category
            text += f"\n{product.category_emoji} **{product.category_name_ar}:**\n"
            text += "─" * 22 + "\n"

        stars = price_to_stars(product.final_price)
        text += f"• **{product.name}**\n"
        text += f"  💰 `{product.final_price}$` | ⭐ `{stars}` نجمة\n"

    text += f"\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"💳 **طرق الدفع:** Stars | TON | PayPal\n"
    text += f"🛒 **للشراء:** اذهب إلى قسم المنتجات"

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )


# ─── Rules Section ────────────────────────────────────────────────────────────

@router.message(F.text == "📝 القوانين")
async def show_rules(message: Message):
    """Display rules and terms of use."""
    user = await get_user(message.from_user.id)
    if not user or user.is_banned:
        return

    await message.answer(
        TextTemplates.RULES_MESSAGE,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )


# ─── Info Section ─────────────────────────────────────────────────────────────

@router.message(F.text == "ℹ️ معلومات")
async def show_info(message: Message):
    """Display store information."""
    user = await get_user(message.from_user.id)
    if not user or user.is_banned:
        return

    info_text = TextTemplates.INFO_MESSAGE.format(
        bot_name=BOT_NAME,
        channel_link=CHANNEL_LINK,
        bot_username=BOT_USERNAME,
    )

    await message.answer(
        info_text,
        parse_mode="Markdown",
        reply_markup=get_support_keyboard(),
        disable_web_page_preview=True,
    )


# ─── Profile Section ──────────────────────────────────────────────────────────

@router.message(F.text == "👤 حسابي")
@router.message(Command("profile"))
async def show_profile(message: Message):
    """Display user profile."""
    user = await get_user(message.from_user.id)
    if not user or user.is_banned:
        return

    membership = "💎 VIP" if user.total_spent >= 50 else "🥈 عادي"
    name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "مستخدم"

    profile_text = TextTemplates.PROFILE_TEMPLATE.format(
        user_id=user.telegram_id,
        name=name,
        reg_date=user.reg_date.strftime("%Y-%m-%d") if user.reg_date else "غير معروف",
        orders_count=user.orders_count,
        total_spent=round(user.total_spent, 2),
        currency="USD",
        referrals_count=user.referral_count,
        membership=membership,
    )

    await message.answer(
        profile_text,
        parse_mode="Markdown",
        reply_markup=get_profile_inline_keyboard(message.from_user.id),
    )


@router.callback_query(F.data.startswith("profile:main:"))
async def callback_profile_main(callback: CallbackQuery):
    """Show profile from inline button."""
    telegram_id = int(callback.data.split(":")[2])

    if callback.from_user.id != telegram_id and not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    user = await get_user(telegram_id)
    if not user:
        await callback.answer("❌ المستخدم غير موجود", show_alert=True)
        return

    membership = "💎 VIP" if user.total_spent >= 50 else "🥈 عادي"
    name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "مستخدم"

    profile_text = TextTemplates.PROFILE_TEMPLATE.format(
        user_id=user.telegram_id,
        name=name,
        reg_date=user.reg_date.strftime("%Y-%m-%d") if user.reg_date else "غير معروف",
        orders_count=user.orders_count,
        total_spent=round(user.total_spent, 2),
        currency="USD",
        referrals_count=user.referral_count,
        membership=membership,
    )

    try:
        await callback.message.edit_text(
            profile_text,
            parse_mode="Markdown",
            reply_markup=get_profile_inline_keyboard(telegram_id),
        )
    except Exception:
        await callback.message.answer(
            profile_text,
            parse_mode="Markdown",
            reply_markup=get_profile_inline_keyboard(telegram_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("profile:orders:"))
async def callback_profile_orders(callback: CallbackQuery):
    """Show order history."""
    telegram_id = int(callback.data.split(":")[2])

    if callback.from_user.id != telegram_id and not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    orders = await get_user_orders(telegram_id, limit=50)

    if not orders:
        text = TextTemplates.NO_ORDERS_MESSAGE
    else:
        text = TextTemplates.ORDER_HISTORY_HEADER
        for order in orders[:10]:
            status_emoji = {
                "pending": "⏳",
                "awaiting_payment": "💳",
                "paid": "💰",
                "processing": "⚙️",
                "completed": "✅",
                "failed": "❌",
                "refunded": "↩️",
            }.get(order.status, "❓")

            payment_emoji = {
                "stars": "⭐",
                "ton": "💎",
                "paypal": "💵",
            }.get(order.payment_method or "", "💳")

            text += (
                f"{status_emoji} **طلب #{order.order_id[:8]}**\n"
                f"📦 {order.product.name if order.product else 'غير معروف'}\n"
                f"{payment_emoji} {order.price_paid}$ | {order.created_at.strftime('%Y-%m-%d')}\n"
                f"─" * 15 + "\n"
            )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_order_history_keyboard(telegram_id, total=len(orders)),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_order_history_keyboard(telegram_id, total=len(orders)),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("profile:referral:"))
async def callback_profile_referral(callback: CallbackQuery):
    """Show referral system info."""
    telegram_id = int(callback.data.split(":")[2])

    if callback.from_user.id != telegram_id and not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    user = await get_user(telegram_id)
    if not user:
        await callback.answer("❌ المستخدم غير موجود", show_alert=True)
        return

    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref{telegram_id}"

    text = TextTemplates.REFERRAL_MESSAGE.format(
        referral_link=referral_link,
        bonus_percent="5",
        referrals_count=user.referral_count,
        total_earnings=user.referral_earnings,
        currency="USD",
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_referral_keyboard(telegram_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_referral_keyboard(telegram_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("profile:deposit:"))
async def callback_profile_deposit(callback: CallbackQuery):
    """Handle balance deposit request."""
    try:
        await callback.message.edit_text(
            "💰 **شحن الرصيد**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 **طرق الدفع المتاحة:**\n"
            "⭐ Telegram Stars - الأسرع والأسهل\n"
            "💎 TON Keeper\n"
            "💵 PayPal\n\n"
            "🛒 لشراء منتج مباشرة، اذهب لقسم المنتجات\n"
            "واختر طريقة الدفع عند الشراء.",
            parse_mode="Markdown",
            reply_markup=get_support_keyboard(),
        )
    except Exception:
        pass
    await callback.answer()


# ─── Support Section ──────────────────────────────────────────────────────────

@router.message(F.text == "🛠 الدعم الفني")
@router.message(Command("support"))
async def show_support(message: Message):
    """Display support information."""
    user = await get_user(message.from_user.id)
    if not user or user.is_banned:
        return

    support_text = TextTemplates.SUPPORT_MESSAGE.format(
        channel_link=CHANNEL_LINK,
    )

    await message.answer(
        support_text,
        parse_mode="Markdown",
        reply_markup=get_support_keyboard(),
    )


# ─── Menu Callbacks ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu:main")
async def callback_menu_main(callback: CallbackQuery):
    """Return to main menu from inline."""
    welcome_text = TextTemplates.WELCOME_MESSAGE.format(
        bot_name=BOT_NAME,
        channel_link=CHANNEL_LINK,
        bot_username=BOT_USERNAME,
    )

    try:
        await callback.message.edit_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_categories_inline_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "menu:categories")
async def callback_menu_categories(callback: CallbackQuery):
    """Return to categories list."""
    try:
        await callback.message.edit_text(
            "🛒 **اختر القسم:**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=get_categories_inline_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            "🛒 **اختر القسم:**",
            parse_mode="Markdown",
            reply_markup=get_categories_inline_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """No-op callback for display-only buttons."""
    await callback.answer()


# ─── Channel Post Generation ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("share_channel:"))
async def callback_share_channel(callback: CallbackQuery):
    """Generate a channel post preview for a product."""
    product_key = callback.data.split(":")[1]
    product = await get_product_by_key(product_key)

    if not product:
        await callback.answer("❌ المنتج غير موجود", show_alert=True)
        return

    image_buffer = generate_channel_post_image(
        product_name=product.name,
        price=str(product.final_price),
        category=f"{product.category_emoji} {product.category_name_ar}",
    )

    deep_link = f"https://t.me/{BOT_USERNAME}?start=buy_{product_key}"
    stars_amount = price_to_stars(product.final_price)

    caption = (
        f"{product.category_emoji} **{product.name}**\n\n"
        f"💰 **السعر:** `{product.final_price}` USD\n"
        f"⭐ أو `{stars_amount}` Telegram Stars\n\n"
        f"✅ توصيل فوري مؤتمت\n"
        f"✅ ضمان كامل\n\n"
        f"🛒 **للشراء:** [اضغط هنا]({deep_link})\n\n"
        f"📢 {CHANNEL_LINK}"
    )

    await callback.message.answer_photo(
        photo=image_buffer,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=get_channel_post_keyboard(product_key),
    )

    await callback.answer("✅ تم إنشاء المنشور!")


# ─── Admin Handlers ───────────────────────────────────────────────────────────

@router.message(F.text == "📊 الإحصائيات")
async def admin_stats(message: Message):
    """Show admin statistics panel."""
    if not is_admin(message.from_user.id):
        return

    stats = await get_full_stats()

    stats_text = TextTemplates.ADMIN_STATS.format(
        total_users=stats["total_users"],
        total_orders=stats["total_orders"],
        total_revenue=stats["total_revenue"],
        today_orders=stats["today_orders"],
        currency="USD",
    )

    stats_text += (
        f"\n📊 **حالة الطلبات:**\n"
        f"⏳ قيد الانتظار: `{stats['pending_orders']}`\n"
        f"⚙️ قيد المعالجة: `{stats['processing_orders']}`\n"
        f"✅ مكتملة: `{stats['completed_orders']}`\n"
        f"❌ فاشلة: `{stats['failed_orders']}`\n"
    )

    await message.answer(
        stats_text,
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard(),
    )

    await log_admin_action(admin_id=message.from_user.id, action="view_stats")


@router.message(F.text == "👥 المستخدمين")
async def admin_users(message: Message):
    """Show recent users list."""
    if not is_admin(message.from_user.id):
        return

    from database import get_all_users
    users = await get_all_users(limit=20)

    if not users:
        await message.answer("📭 لا يوجد مستخدمون.")
        return

    text = "👥 **المستخدمون الأخيرون:**\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for user in users:
        status = "🚫" if user.is_banned else "✅"
        name = escape_markdown(user.first_name or "مستخدم")
        username = f"@{user.username}" if user.username else "بدون يوزر"
        text += (
            f"{status} `{user.telegram_id}` | {name}\n"
            f"👤 {username} | 📊 طلبات: {user.orders_count}\n"
            f"─" * 15 + "\n"
        )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard(),
    )


@router.message(F.text == "📦 إدارة الطلبات")
async def admin_orders(message: Message):
    """Show pending orders for admin action."""
    if not is_admin(message.from_user.id):
        return

    orders = await get_pending_orders()

    if not orders:
        await message.answer(
            "📭 **لا يوجد طلبات تحتاج مراجعة.**\n\n"
            "جميع الطلبات تمت معالجتها! ✅",
            parse_mode="Markdown",
            reply_markup=get_admin_menu_keyboard(),
        )
        return

    text = f"📦 **الطلبات المعلقة ({len(orders)}):**\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for order in orders[:5]:
        payment_emoji = {"stars": "⭐", "ton": "💎", "paypal": "💵"}.get(order.payment_method or "", "💳")
        text += (
            f"🆔 `{order.order_id[:10]}`\n"
            f"📦 {order.product.name if order.product else '؟'}\n"
            f"{payment_emoji} {order.price_paid}$ | 👤 `{order.user_id}`\n"
            f"─" * 15 + "\n"
        )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_admin_pending_orders_keyboard(orders),
    )


@router.callback_query(F.data.startswith("admin:order_detail:"))
async def callback_admin_order_detail(callback: CallbackQuery):
    """Show detailed order info for admin."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    payment_emoji = {"stars": "⭐", "ton": "💎", "paypal": "💵"}.get(order.payment_method or "", "💳")
    product_name = order.product.name if order.product else "؟"
    user_name = order.user.first_name if order.user else "؟"

    text = (
        f"📦 **تفاصيل الطلب**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 **الطلب:** `{order_id}`\n"
        f"📦 **المنتج:** {product_name}\n"
        f"👤 **المستخدم:** {user_name} (`{order.user_id}`)\n"
        f"{payment_emoji} **طريقة الدفع:** {order.payment_method or 'غير محدد'}\n"
        f"💰 **المبلغ:** {order.price_paid} USD\n"
        f"📊 **الحالة:** {order.status}\n"
        f"📅 **التاريخ:** {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚠️ **اختر الإجراء:**"
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_order_action_keyboard(order_id, order.user_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_order_action_keyboard(order_id, order.user_id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("order:deliver:"))
async def callback_order_deliver(callback: CallbackQuery, state: FSMContext):
    """Start manual delivery flow."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    await state.set_state(DeliveryState.waiting_apple_id)
    await state.update_data(order_id=order_id, user_id=order.user_id)

    await callback.message.answer(
        f"📧 **توصيل الطلب `{order_id[:10]}`**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"أرسل **Apple ID (البريد الإلكتروني):**\n\n"
        f"(أرسل ❌ إلغاء للتراجع)",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()


@router.message(DeliveryState.waiting_apple_id)
async def delivery_get_apple_id(message: Message, state: FSMContext):
    """Get Apple ID from admin."""
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("❌ تم الإلغاء.", reply_markup=get_admin_menu_keyboard())
        return

    await state.update_data(apple_id=message.text.strip())
    await state.set_state(DeliveryState.waiting_password)

    await message.answer(
        f"✅ Apple ID: `{message.text.strip()}`\n\n"
        f"الآن أرسل **كلمة المرور:**",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(DeliveryState.waiting_password)
async def delivery_get_password(message: Message, state: FSMContext, bot: Bot):
    """Get password and complete delivery."""
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("❌ تم الإلغاء.", reply_markup=get_admin_menu_keyboard())
        return

    data = await state.get_data()
    order_id = data.get("order_id")
    apple_id = data.get("apple_id")
    password = message.text.strip()

    await state.clear()

    # Deliver the order
    order = await deliver_order(
        order_id=order_id,
        apple_id=apple_id,
        apple_password=password,
        admin_id=message.from_user.id,
    )

    if not order:
        await message.answer("❌ حدث خطأ في توصيل الطلب.", reply_markup=get_admin_menu_keyboard())
        return

    product_name = order.product.name if order.product else "المنتج"

    # Send delivery message to user
    delivery_text = TextTemplates.DELIVERY_MESSAGE.format(
        product_name=product_name,
        order_id=order_id,
        apple_id=apple_id,
        password=password,
    )

    try:
        await bot.send_message(
            chat_id=order.user_id,
            text=delivery_text,
            parse_mode="Markdown",
        )
        delivery_sent = True
    except Exception as e:
        logger.error(f"Could not deliver to user {order.user_id}: {e}")
        delivery_sent = False

    # Confirm to admin
    status_text = "✅ تم الإرسال للعميل!" if delivery_sent else "⚠️ لم يتمكن من إرسال الرسالة للعميل"
    await message.answer(
        f"✅ **تم توصيل الطلب بنجاح!**\n\n"
        f"🆔 الطلب: `{order_id}`\n"
        f"📦 المنتج: {product_name}\n"
        f"👤 العميل: `{order.user_id}`\n"
        f"📧 Apple ID: `{apple_id}`\n\n"
        f"{status_text}",
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard(),
    )

    await log_admin_action(
        admin_id=message.from_user.id,
        action="deliver_order",
        target_user_id=order.user_id,
        details=f"Delivered order {order_id}",
    )


@router.callback_query(F.data.startswith("order:refund:"))
async def callback_order_refund(callback: CallbackQuery, bot: Bot):
    """Refund an order."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    order_id = callback.data.split(":")[2]
    order = await get_order(order_id)

    if not order:
        await callback.answer("❌ الطلب غير موجود", show_alert=True)
        return

    success = await refund_order(order_id, admin_id=callback.from_user.id)

    if success:
        # Notify user
        try:
            await bot.send_message(
                chat_id=order.user_id,
                text=f"↩️ **تم استرداد طلبك**\n\n"
                     f"🆔 رقم الطلب: `{order_id}`\n"
                     f"📦 المنتج: {order.product.name if order.product else '؟'}\n\n"
                     f"تواصل مع الدعم لمزيد من المعلومات.",
                parse_mode="Markdown",
            )
        except Exception:
            pass

        await callback.answer("✅ تم الاسترداد وإشعار العميل", show_alert=True)
        try:
            await callback.message.edit_text(
                f"↩️ **تم استرداد الطلب `{order_id[:10]}`**",
                parse_mode="Markdown",
                reply_markup=get_admin_menu_keyboard(),
            )
        except Exception:
            pass
    else:
        await callback.answer("❌ فشل الاسترداد", show_alert=True)


@router.callback_query(F.data.startswith("admin:view_user:"))
async def callback_admin_view_user(callback: CallbackQuery):
    """View user details from admin panel."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    user_id = int(callback.data.split(":")[2])
    user = await get_user(user_id)

    if not user:
        await callback.answer("❌ المستخدم غير موجود", show_alert=True)
        return

    name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "مستخدم"
    status = "🚫 محظور" if user.is_banned else "✅ نشط"

    text = (
        f"👤 **بيانات المستخدم**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 `{user.telegram_id}`\n"
        f"👤 {name}\n"
        f"📊 الحالة: {status}\n"
        f"📦 الطلبات: {user.orders_count}\n"
        f"💰 المشتريات: {user.total_spent}$\n"
        f"📅 التسجيل: {user.reg_date.strftime('%Y-%m-%d') if user.reg_date else '؟'}\n"
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_admin_actions_keyboard(user_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_admin_actions_keyboard(user_id),
        )
    await callback.answer()


@router.message(F.text == "📢 إشعار عام")
async def admin_broadcast_start(message: Message, state: FSMContext):
    """Start broadcast flow."""
    if not is_admin(message.from_user.id):
        return

    await state.set_state(BroadcastState.waiting_message)
    await message.answer(
        "📢 **إرسال إشعار عام**\n\n"
        "أرسل الرسالة التي تريد إذاعتها لجميع المستخدمين:\n\n"
        "(أرسل ❌ إلغاء للتراجع)",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(BroadcastState.waiting_message)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    """Send broadcast to all users."""
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("❌ تم الإلغاء.", reply_markup=get_admin_menu_keyboard())
        return

    await state.clear()

    from database import get_all_users
    users = await get_all_users(limit=10000)

    sent = 0
    failed = 0

    status_msg = await message.answer(
        f"⏳ جاري الإرسال... (0/{len(users)})",
        reply_markup=get_admin_menu_keyboard(),
    )

    for user in users:
        try:
            await bot.copy_message(
                chat_id=user.telegram_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            sent += 1
        except Exception:
            failed += 1

        if (sent + failed) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"⏳ جاري الإرسال... ({sent + failed}/{len(users)})\n"
                    f"✅ نجح: {sent} | ❌ فشل: {failed}"
                )
            except Exception:
                pass

    await status_msg.edit_text(
        f"✅ **تم الإرسال!**\n\n"
        f"✅ نجح: {sent}\n"
        f"❌ فشل: {failed}\n"
        f"📊 المجموع: {len(users)}"
    )

    await log_admin_action(
        admin_id=message.from_user.id,
        action="broadcast",
        details=f"Sent to {sent} users, failed {failed}",
    )


@router.message(F.text == "🚫 حظر مستخدم")
async def admin_ban_start(message: Message, state: FSMContext):
    """Start ban user flow."""
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AdminActionState.waiting_user_id)
    await state.update_data(action="ban")
    await message.answer(
        "🚫 **حظر مستخدم**\n\n"
        "أرسل Telegram ID للمستخدم:\n\n"
        "(أرسل ❌ إلغاء للتراجع)",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AdminActionState.waiting_user_id)
async def admin_action_execute(message: Message, state: FSMContext):
    """Execute admin action on user."""
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("❌ تم الإلغاء.", reply_markup=get_admin_menu_keyboard())
        return

    data = await state.get_data()
    action = data.get("action", "ban")

    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ يرجى إرسال رقم ID صحيح.")
        return

    await state.clear()

    if action == "ban":
        success = await ban_user(target_id)
        result_text = f"✅ تم حظر المستخدم `{target_id}`" if success else f"❌ المستخدم `{target_id}` غير موجود"
    else:
        success = await unban_user(target_id)
        result_text = f"✅ تم فك حظر المستخدم `{target_id}`" if success else f"❌ المستخدم `{target_id}` غير موجود"

    await message.answer(result_text, parse_mode="Markdown", reply_markup=get_admin_menu_keyboard())

    if success:
        await log_admin_action(
            admin_id=message.from_user.id,
            action=action,
            target_user_id=target_id,
        )


@router.message(F.text == "⚙️ إعدادات المتجر")
async def admin_settings(message: Message):
    """Show store settings."""
    if not is_admin(message.from_user.id):
        return

    from config import PROFIT_MARGIN_PERCENT, EXCHANGE_RATE_RUB_TO_USD, TON_WALLET_ADDRESS, PAYPAL_EMAIL

    await message.answer(
        "⚙️ **إعدادات المتجر**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💹 **هامش الربح:** `{PROFIT_MARGIN_PERCENT}%`\n"
        f"💱 **سعر الصرف:** `{EXCHANGE_RATE_RUB_TO_USD}` USD/RUB\n\n"
        f"💎 **محفظة TON:** `{TON_WALLET_ADDRESS or 'غير مضبوطة'}`\n"
        f"💵 **PayPal:** `{PAYPAL_EMAIL or 'غير مضبوط'}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔧 لتعديل الإعدادات، عدّل متغيرات البيئة في الخادم.",
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard(),
    )


# ─── Admin Callbacks ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:ban:"))
async def callback_admin_ban(callback: CallbackQuery):
    """Ban user from admin action."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    target_id = int(callback.data.split(":")[2])
    success = await ban_user(target_id)

    if success:
        await callback.answer(f"✅ تم حظر المستخدم {target_id}", show_alert=True)
        await log_admin_action(callback.from_user.id, "ban_user", target_id)
    else:
        await callback.answer("❌ المستخدم غير موجود", show_alert=True)


@router.callback_query(F.data.startswith("admin:unban:"))
async def callback_admin_unban(callback: CallbackQuery):
    """Unban user from admin action."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    target_id = int(callback.data.split(":")[2])
    success = await unban_user(target_id)

    if success:
        await callback.answer(f"✅ تم فك حظر المستخدم {target_id}", show_alert=True)
        await log_admin_action(callback.from_user.id, "unban_user", target_id)
    else:
        await callback.answer("❌ المستخدم غير موجود", show_alert=True)


@router.callback_query(F.data == "admin:panel")
async def callback_admin_panel(callback: CallbackQuery):
    """Return to admin panel."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ غير مصرح", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            "🔧 **لوحة الإدارة**\n\nاختر الإجراء:",
            parse_mode="Markdown",
        )
    except Exception:
        pass
    await callback.answer()


# ─── Error Handler ────────────────────────────────────────────────────────────

@router.errors()
async def error_handler(event, exception: Exception):
    """Global error handler."""
    logger.error(f"Handler error: {exception}", exc_info=True)
