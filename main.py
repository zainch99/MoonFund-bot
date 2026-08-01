import os
import json
import logging
import asyncio
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CRYPTO_BOT_TOKEN = os.getenv("CRYPTO_BOT_TOKEN")

# Flask App setup
app = Flask(__name__)
CORS(app)

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Welcome to MoonFund Bot! Tap 'Open App' below to view evaluation packages.")

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        
        if data.get("action") == "buy_package":
            pkg = data.get("package_name")
            fee = data.get("fee_usd")
            
            text = (
                f"🎯 **Selected Package:** {pkg}\n"
                f"💵 **Evaluation Fee:** ${fee} USD\n\n"
                f"To activate your account, send payment via SOL / USDC to your personal deposit address.\n\n"
                f"⚠️ *Trading dashboard access will unlock automatically after payment confirmation.*"
            )
            await update.effective_message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error handling webapp data: {e}")

# Flask Web Server Routes (For Payment API)
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "MoonFund Backend API is Running"}), 200

@app.route('/api/create-invoice', methods=['POST'])
def create_invoice():
    try:
        data = request.json
        amount = data.get('amount')
        title = data.get('title', 'MoonFund Challenge')

        if not CRYPTO_BOT_TOKEN:
            return jsonify({"ok": False, "error": {"name": "CRYPTO_BOT_TOKEN Missing"}}), 500

        # Request to Crypto Pay API
        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}
        payload = {
            "asset": "USDT",
            "amount": str(amount),
            "description": f"Payment for {title}",
            "paid_btn_name": "callback",
            "paid_btn_url": "https://t.me/MoonFund"
        }

        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        return jsonify(res_data)

    except Exception as e:
        logging.error(f"Invoice Error: {e}")
        return jsonify({"ok": False, "error": {"name": str(e)}}), 500

# Function to run Telegram Bot along with Flask
def run_telegram_bot():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN missing!")
        return
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    print("Telegram Bot is running...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    import threading
    
    # Run Telegram Bot in a background thread
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Run Flask Web Server on Railway Port
    port = int(os.environ.get("PORT", 3000))
    print(f"Flask Server starting on port {port}...")
    app.run(host="0.0.0.0", port=port)
