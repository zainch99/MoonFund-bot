import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from supabase import create_client, Client

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""

    try:
        # Check if user exists in Supabase, if not insert
        res = supabase.table("users").upsert({
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name
        }).execute()
        
    except Exception as e:
        logging.error(f"Database error: {e}")

    # WebApp URL placeholder (we will update this when frontend is deployed)
    web_app_url = "https://example.com" 

    keyboard = [
        [InlineKeyboardButton("🚀 Launch Trading App", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Welcome **{first_name}** to MoonFund Evaluation App! 📈\n\n"
        "Click below to open your evaluation account dashboard and start trading.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN is missing!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
