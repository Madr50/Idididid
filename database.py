"""
Appify Store Bot - Database Module (v2.0 PREMIUM)
=================================================
Async SQLAlchemy ORM with SQLite (PostgreSQL-ready).
Handles Users, Orders, Products, and Referrals with full CRUD operations.
Enhanced with multi-payment support and automated delivery tracking.
"""

import datetime
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, BigInteger, String, Float,
    DateTime, Boolean, Text, ForeignKey, select, func, desc, update
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship, selectinload
from sqlalchemy.exc import IntegrityError

from config import DATABASE_PATH, PRODUCT_CATALOG, get_all_products

# ─── Database Engine & Session ────────────────────────────────────────────────
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


# ─── Models ───────────────────────────────────────────────────────────────────

class User(Base):
    """Telegram user model with profile and referral tracking."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(128), nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    language_code = Column(String(10), default="ar")
    reg_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_banned = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    referred_by = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=True)
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    orders_count = Column(Integer, default=0)

    # Relationships
    orders = relationship("Order", back_populates="user", lazy="selectin")
    referrals = relationship(
        "User",
        backref="referrer",
        remote_side=[telegram_id],
        foreign_keys=[referred_by],
        lazy="selectin"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "reg_date": self.reg_date.strftime("%Y-%m-%d") if self.reg_date else None,
            "is_banned": self.is_banned,
            "is_admin": self.is_admin,
            "referral_count": self.referral_count,
            "referral_earnings": self.referral_earnings,
            "total_spent": self.total_spent,
            "orders_count": self.orders_count,
        }


class Product(Base):
    """Product catalog model with dynamic pricing and images."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_key = Column(String(64), unique=True, nullable=False, index=True)
    category = Column(String(32), nullable=False)
    category_emoji = Column(String(8), nullable=False)
    category_name_ar = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    name_ar = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    base_price_rub = Column(Integer, nullable=False)
    final_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="product", lazy="selectin")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "product_key": self.product_key,
            "category": self.category,
            "category_emoji": self.category_emoji,
            "category_name_ar": self.category_name_ar,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "base_price_rub": self.base_price_rub,
            "final_price": self.final_price,
            "is_active": self.is_active,
            "image_url": self.image_url,
        }


class Order(Base):
    """Order model tracking purchase lifecycle with multi-payment support."""
    __tablename__ = "orders"

    STATUS_PENDING = "pending"
    STATUS_AWAITING_PAYMENT = "awaiting_payment"
    STATUS_PAID = "paid"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"

    PAYMENT_STARS = "stars"
    PAYMENT_TON = "ton"
    PAYMENT_PAYPAL = "paypal"
    PAYMENT_MANUAL = "manual"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    status = Column(String(32), default=STATUS_PENDING)
    payment_method = Column(String(16), nullable=True)  # stars / ton / paypal
    price_paid = Column(Float, nullable=False)
    currency = Column(String(8), default="USD")
    stars_amount = Column(Integer, nullable=True)       # Stars amount if paid with Stars
    ton_amount = Column(Float, nullable=True)           # TON amount if paid with TON
    payment_proof = Column(Text, nullable=True)         # Screenshot or tx hash
    apple_id = Column(String(256), nullable=True)
    apple_password = Column(String(256), nullable=True)
    source_order_response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders", lazy="selectin")
    product = relationship("Product", back_populates="orders", lazy="selectin")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "product_name": self.product.name if self.product else None,
            "status": self.status,
            "payment_method": self.payment_method,
            "price_paid": self.price_paid,
            "currency": self.currency,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M") if self.completed_at else None,
        }


class AdminLog(Base):
    """Admin action log for auditing."""
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(64), nullable=False)
    target_user_id = Column(BigInteger, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ─── Database Initialization ──────────────────────────────────────────────────

async def init_db():
    """Initialize database tables and seed products."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_products()
    print("[DB] Database initialized and products seeded.")


async def seed_products():
    """Seed the database with initial product catalog (with images & descriptions)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        existing = result.scalars().all()

        if existing:
            # Update existing products with new image_url and description if missing
            for product_data in get_all_products():
                stmt = (
                    update(Product)
                    .where(Product.product_key == product_data["id"])
                    .values(
                        image_url=product_data.get("image_url", ""),
                        description=product_data.get("description", ""),
                        name_ar=product_data.get("name_ar", product_data["name"]),
                        final_price=product_data["final_price"],
                    )
                )
                await session.execute(stmt)
            await session.commit()
            print(f"[DB] Updated {len(existing)} existing products with images.")
            return

        # Seed fresh products
        for product_data in get_all_products():
            product = Product(
                product_key=product_data["id"],
                category=product_data["category"],
                category_emoji=product_data["category_emoji"],
                category_name_ar=product_data["category_name_ar"],
                name=product_data["name"],
                name_ar=product_data.get("name_ar", product_data["name"]),
                description=product_data.get("description", ""),
                base_price_rub=product_data["base_price_rub"],
                final_price=product_data["final_price"],
                image_url=product_data.get("image_url", ""),
                is_active=True,
            )
            session.add(product)

        await session.commit()
        print(f"[DB] Seeded {len(get_all_products())} products with images.")


# ─── CRUD Operations: Users ───────────────────────────────────────────────────

async def get_user(telegram_id: int) -> Optional[User]:
    """Get user by Telegram ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def get_or_create_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_code: str = "ar",
    referrer_id: Optional[int] = None,
) -> User:
    """Get existing user or create new one."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Update user info
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            await session.commit()
            return user

        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            referred_by=referrer_id,
        )
        session.add(user)

        # Update referrer count
        if referrer_id:
            referrer_result = await session.execute(
                select(User).where(User.telegram_id == referrer_id)
            )
            referrer = referrer_result.scalar_one_or_none()
            if referrer:
                referrer.referral_count += 1

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

        return user


async def get_all_users(limit: int = 100) -> List[User]:
    """Get all users ordered by registration date."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).order_by(desc(User.reg_date)).limit(limit)
        )
        return result.scalars().all()


async def ban_user(telegram_id: int) -> bool:
    """Ban a user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.is_banned = True
        await session.commit()
        return True


async def unban_user(telegram_id: int) -> bool:
    """Unban a user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.is_banned = False
        await session.commit()
        return True


# ─── CRUD Operations: Products ────────────────────────────────────────────────

async def get_all_products_db() -> List[Product]:
    """Get all active products."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product).where(Product.is_active == True).order_by(Product.category, Product.id)
        )
        return result.scalars().all()


async def get_product_by_key(product_key: str) -> Optional[Product]:
    """Get product by its unique key."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product).where(Product.product_key == product_key)
        )
        return result.scalar_one_or_none()


async def get_product_by_id(product_id: int) -> Optional[Product]:
    """Get product by database ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()


async def update_product_image(product_key: str, image_url: str) -> bool:
    """Update product image URL."""
    async with AsyncSessionLocal() as session:
        stmt = (
            update(Product)
            .where(Product.product_key == product_key)
            .values(image_url=image_url)
        )
        await session.execute(stmt)
        await session.commit()
        return True


# ─── CRUD Operations: Orders ──────────────────────────────────────────────────

def generate_order_id() -> str:
    """Generate a unique order ID."""
    return str(uuid.uuid4()).replace("-", "")[:16].upper()


async def create_order(
    telegram_id: int,
    product_id: int,
    price_paid: float,
    currency: str = "USD",
    payment_method: Optional[str] = None,
) -> Optional[Order]:
    """Create a new order."""
    async with AsyncSessionLocal() as session:
        order = Order(
            order_id=generate_order_id(),
            user_id=telegram_id,
            product_id=product_id,
            price_paid=price_paid,
            currency=currency,
            payment_method=payment_method,
            status=Order.STATUS_PENDING,
        )
        session.add(order)
        try:
            await session.commit()
            # Reload with relationships
            result = await session.execute(
                select(Order)
                .options(selectinload(Order.product), selectinload(Order.user))
                .where(Order.order_id == order.order_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            await session.rollback()
            print(f"[DB] Error creating order: {e}")
            return None


async def get_order(order_id: str) -> Optional[Order]:
    """Get order by order ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.product), selectinload(Order.user))
            .where(Order.order_id == order_id)
        )
        return result.scalar_one_or_none()


async def get_user_orders(telegram_id: int, limit: int = 20) -> List[Order]:
    """Get all orders for a user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.product))
            .where(Order.user_id == telegram_id)
            .order_by(desc(Order.created_at))
            .limit(limit)
        )
        return result.scalars().all()


async def get_recent_orders(limit: int = 20, status: Optional[str] = None) -> List[Order]:
    """Get recent orders, optionally filtered by status."""
    async with AsyncSessionLocal() as session:
        query = (
            select(Order)
            .options(selectinload(Order.product), selectinload(Order.user))
            .order_by(desc(Order.created_at))
            .limit(limit)
        )
        if status:
            query = query.where(Order.status == status)
        result = await session.execute(query)
        return result.scalars().all()


async def get_pending_orders() -> List[Order]:
    """Get all orders awaiting admin action (paid but not delivered)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.product), selectinload(Order.user))
            .where(Order.status.in_([Order.STATUS_PAID, Order.STATUS_PROCESSING]))
            .order_by(Order.created_at)
        )
        return result.scalars().all()


async def update_order_status(
    order_id: str,
    status: str,
    payment_method: Optional[str] = None,
    error_message: Optional[str] = None,
    admin_note: Optional[str] = None,
) -> bool:
    """Update order status."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return False

        order.status = status
        if payment_method:
            order.payment_method = payment_method
        if error_message:
            order.error_message = error_message
        if admin_note:
            order.admin_note = admin_note

        if status == Order.STATUS_PAID:
            order.paid_at = datetime.datetime.utcnow()
        elif status == Order.STATUS_COMPLETED:
            order.completed_at = datetime.datetime.utcnow()
        elif status == Order.STATUS_REFUNDED:
            order.refunded_at = datetime.datetime.utcnow()

        await session.commit()
        return True


async def set_order_payment_info(
    order_id: str,
    payment_method: str,
    stars_amount: Optional[int] = None,
    ton_amount: Optional[float] = None,
) -> bool:
    """Set payment method details on an order."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return False

        order.payment_method = payment_method
        order.status = Order.STATUS_AWAITING_PAYMENT
        if stars_amount:
            order.stars_amount = stars_amount
        if ton_amount:
            order.ton_amount = ton_amount

        await session.commit()
        return True


async def deliver_order(
    order_id: str,
    apple_id: str,
    apple_password: str,
    admin_id: Optional[int] = None,
) -> Optional[Order]:
    """Mark order as delivered with Apple ID credentials."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.product), selectinload(Order.user))
            .where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return None

        order.apple_id = apple_id
        order.apple_password = apple_password
        order.status = Order.STATUS_COMPLETED
        order.completed_at = datetime.datetime.utcnow()
        order.delivered_at = datetime.datetime.utcnow()

        # Update user stats
        user_result = await session.execute(
            select(User).where(User.telegram_id == order.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.total_spent += order.price_paid
            user.orders_count += 1

        await session.commit()

        # Log admin action
        if admin_id:
            log = AdminLog(
                admin_id=admin_id,
                action="deliver_order",
                target_user_id=order.user_id,
                details=f"Order {order_id} delivered",
            )
            session.add(log)
            await session.commit()

        return order


async def refund_order(order_id: str, admin_id: Optional[int] = None) -> bool:
    """Mark order as refunded."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return False

        order.status = Order.STATUS_REFUNDED
        order.refunded_at = datetime.datetime.utcnow()
        await session.commit()

        if admin_id:
            log = AdminLog(
                admin_id=admin_id,
                action="refund_order",
                target_user_id=order.user_id,
                details=f"Order {order_id} refunded",
            )
            session.add(log)
            await session.commit()

        return True


# ─── Statistics ───────────────────────────────────────────────────────────────

async def get_full_stats() -> Dict[str, Any]:
    """Get comprehensive store statistics."""
    async with AsyncSessionLocal() as session:
        total_users = await session.scalar(select(func.count(User.id)))
        total_orders = await session.scalar(select(func.count(Order.id)))
        total_revenue = await session.scalar(
            select(func.sum(Order.price_paid)).where(Order.status == Order.STATUS_COMPLETED)
        ) or 0.0

        today = datetime.datetime.utcnow().date()
        today_orders = await session.scalar(
            select(func.count(Order.id)).where(
                func.date(Order.created_at) == today
            )
        ) or 0

        pending_orders = await session.scalar(
            select(func.count(Order.id)).where(Order.status == Order.STATUS_PENDING)
        ) or 0

        processing_orders = await session.scalar(
            select(func.count(Order.id)).where(
                Order.status.in_([Order.STATUS_PAID, Order.STATUS_PROCESSING])
            )
        ) or 0

        completed_orders = await session.scalar(
            select(func.count(Order.id)).where(Order.status == Order.STATUS_COMPLETED)
        ) or 0

        failed_orders = await session.scalar(
            select(func.count(Order.id)).where(Order.status == Order.STATUS_FAILED)
        ) or 0

        return {
            "total_users": total_users or 0,
            "total_orders": total_orders or 0,
            "total_revenue": round(total_revenue, 2),
            "today_orders": today_orders,
            "pending_orders": pending_orders,
            "processing_orders": processing_orders,
            "completed_orders": completed_orders,
            "failed_orders": failed_orders,
        }


# ─── Admin Logging ────────────────────────────────────────────────────────────

async def log_admin_action(
    admin_id: int,
    action: str,
    target_user_id: Optional[int] = None,
    details: Optional[str] = None,
) -> None:
    """Log an admin action."""
    async with AsyncSessionLocal() as session:
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            target_user_id=target_user_id,
            details=details,
        )
        session.add(log)
        await session.commit()
