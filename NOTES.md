# Bot Project Notes

## GitHub Repo
https://github.com/Madr50/Idididid.git

## Key Files Modified
- config.py - Product catalog with images, payment config (Stars/TON/PayPal)
- database.py - Enhanced schema with payment_method, stars_amount, ton_amount, delivered_at
- frontend/handlers.py - Full payment flow, automated delivery, admin panel
- frontend/keyboards.py - Numbered buttons, back navigation, payment keyboards
- utils/image_watermark.py - urllib-based image download (no aiohttp)

## Payment Methods
- Telegram Stars: via send_invoice with XTR currency
- TON Keeper: manual send to wallet, admin confirms
- PayPal: manual send to email, admin confirms

## Delivery Flow
1. User buys → order created
2. User pays (Stars/TON/PayPal) → admin notified
3. Admin clicks "deliver" → enters Apple ID + password
4. Bot auto-sends credentials to user

## Environment Variables Needed
- BOT_TOKEN
- ADMIN_IDS (comma-separated)
- TON_WALLET_ADDRESS
- PAYPAL_EMAIL
- PYROGRAM_API_ID, PYROGRAM_API_HASH, PYROGRAM_SESSION_STRING (optional)
