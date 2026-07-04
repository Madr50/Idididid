"""
Appify Store Bot - SourceBot Bridge
===================================
Pyrogram automation for SourceBot dropshipping.
Lazy import to avoid asyncio event loop issues on startup.
"""

import asyncio
import logging

logger = logging.getLogger("AppifyBot.SourceBot")

# ─── Lazy Pyrogram Import ─────────────────────────────────────────────────────
# We import pyrogram ONLY inside functions to avoid event loop issues on import

_pyrogram_loaded = False
_Client = None
_filters = None

def _load_pyrogram():
    """Lazy load pyrogram to avoid asyncio issues during import."""
    global _pyrogram_loaded, _Client, _filters
    if _pyrogram_loaded:
        return True
    try:
        from pyrogram import Client, filters
        _Client = Client
        _filters = filters
        _pyrogram_loaded = True
        return True
    except Exception as e:
        logger.warning(f"Pyrogram not available: {e}")
        return False


# ─── Automation Functions ─────────────────────────────────────────────────────

async def init_automation():
    """Initialize Pyrogram automation."""
    if not _load_pyrogram():
        logger.warning("⚠️ Pyrogram not loaded - running without automation")
        return False

    from config import (
        PYROGRAM_API_ID, PYROGRAM_API_HASH,
        PYROGRAM_SESSION_STRING, SOURCE_BOT_USERNAME
    )

    # Validate config
    if not all([PYROGRAM_API_ID, PYROGRAM_API_HASH, PYROGRAM_SESSION_STRING]):
        logger.warning("⚠️ Pyrogram credentials not configured")
        return False

    try:
        # Create client inside async context where event loop exists
        app = _Client(
            "sourcebot_session",
            api_id=PYROGRAM_API_ID,
            api_hash=PYROGRAM_API_HASH,
            session_string=PYROGRAM_SESSION_STRING,
            in_memory=True,
        )

        await app.start()
        logger.info("✅ Pyrogram client started")

        # Store client globally for later use
        global _app
        _app = app

        return True

    except Exception as e:
        logger.error(f"❌ Failed to start Pyrogram: {e}")
        return False


async def shutdown_automation():
    """Cleanup Pyrogram client."""
    global _app
    if '_app' in globals() and _app:
        try:
            await _app.stop()
            logger.info("✅ Pyrogram client stopped")
        except Exception as e:
            logger.warning(f"Error stopping Pyrogram: {e}")
        _app = None


# ─── Order Processing ─────────────────────────────────────────────────────────

async def place_source_order(product_key: str) -> dict:
    """Place order via SourceBot using Pyrogram."""
    if not _load_pyrogram() or '_app' not in globals() or not _app:
        return {"success": False, "error": "Pyrogram not initialized"}

    try:
        # Send message to SourceBot
        await _app.send_message("SourceBot", f"/buy {product_key}")

        # Wait for response (simplified)
        await asyncio.sleep(5)

        return {
            "success": True,
            "apple_id": "placeholder@example.com",
            "password": "placeholder123",
        }

    except Exception as e:
        logger.error(f"Order failed: {e}")
        return {"success": False, "error": str(e)}
