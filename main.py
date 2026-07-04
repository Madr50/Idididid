"""
Appify Store Bot - Async Entry Point
====================================
Main asyncio entry point that runs Aiogram Bot, Pyrogram Userbot,
and Flask Keep-Alive server concurrently.
"""

import asyncio
import logging
import signal
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import BOT_TOKEN, validate_config, LOG_LEVEL
from database import init_db
from frontend.handlers import router as frontend_router
from server import run_flask_app, update_status, ping

# ─── Logging Setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger("AppifyBot")


# ─── Bot & Dispatcher ─────────────────────────────────────────────────────────

bot: Bot | None = None
dp: Dispatcher | None = None


# ─── Lifecycle Management ─────────────────────────────────────────────────────

async def on_startup():
    """Startup hook - initialize all components."""
    logger.info("🚀 Starting Appify Store Bot...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Validate configuration
    config_valid = validate_config()
    if config_valid:
        # Lazy import to avoid asyncio event loop issues on startup
        from backend.sourcebot_bridge import init_automation
        automation_ready = await init_automation()
        if automation_ready:
            logger.info("✅ SourceBot automation ready")
        else:
            logger.warning("⚠️ SourceBot automation not available - bot will work in manual mode")
    else:
        logger.warning("⚠️ Running in limited mode without Pyrogram automation")

    # Set bot commands
    await bot.set_my_commands([
        ("start", "بدء البوت / Start the bot"),
        ("menu", "القائمة الرئيسية / Main menu"),
        ("profile", "حسابي / My profile"),
        ("support", "الدعم الفني / Support"),
        ("rules", "القوانين / Rules"),
    ])

    # Notify admins that bot is online
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "🟢 **البوت يعمل الآن!**\n\n"
                "✅ جميع الأنظمة جاهزة.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.warning(f"Could not notify admin {admin_id}: {e}")

    update_status("running")
    logger.info("✅ Bot is running!")


async def on_shutdown():
    """Shutdown hook - cleanup resources."""
    logger.info("🛑 Shutting down Appify Store Bot...")

    update_status("shutting_down")

    # Lazy import to avoid asyncio event loop issues
    from backend.sourcebot_bridge import shutdown_automation
    await shutdown_automation()
    logger.info("✅ Automation shutdown complete")

    # Close bot session
    await bot.session.close()
    logger.info("✅ Bot session closed")

    logger.info("👋 Goodbye!")


# ─── Main Entry Point ─────────────────────────────────────────────────────────

async def main():
    """Main async entry point."""
    global bot, dp

    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()

    # Register routers
    dp.include_router(frontend_router)

    # Register lifecycle hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    # Start all services concurrently
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        await on_shutdown()


async def shutdown():
    """Trigger graceful shutdown."""
    if dp:
        await dp.stop_polling()


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("  Appify Store Bot - Telegram Dropshipping System")
    logger.info("=" * 50)

    # Start Flask keep-alive server in background thread
    try:
        import threading
        flask_thread = threading.Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        logger.info("✅ Flask keep-alive server started")
    except Exception as e:
        logger.warning(f"⚠️ Flask server not started: {e}")

    # Run the main bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
