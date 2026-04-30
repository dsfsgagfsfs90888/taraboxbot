import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread

# Simple server to keep Render happy
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!"

def run_server():
    # Render provides a PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Bot Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot is Live and Ready!")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("CRITICAL ERROR: BOT_TOKEN is missing in Environment Variables!")
        return

    # Start the web server in the background
    Thread(target=run_server, daemon=True).start()

    # Setup and Start the Telegram Bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    print("Starting bot polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
