import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Minimal web server to satisfy Render's health check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Bot logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Bot is Live!")

async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("Error: Please set the BOT_TOKEN in Environment Variables.")
        return

    # Start the web server in a separate thread
    threading.Thread(target=run_health_server, daemon=True).start()

    # Build and start the Telegram Bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    print("Bot is starting...")
    
    # Using run_polling directly works fine as long as the web server is running
    await application.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
