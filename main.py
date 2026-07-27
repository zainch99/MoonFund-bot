import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

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

if __name__ == "__main__":
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN missing!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    print("Bot is running...")
    app.run_polling()
