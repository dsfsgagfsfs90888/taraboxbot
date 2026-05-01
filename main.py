import os
import requests
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask setup
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Get tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text
    if "terabox" in user_url or "nephobox" in user_url:
        status_msg = await update.message.reply_text("⏳ Processing... please wait.")
        api_url = f"https://api.apify.com/v2/acts/easyapi~terabox-video-file-downloader/runs?token={APIFY_TOKEN}"
        payload = {"teraboxUrls": [user_url]}
        try:
            run_req = requests.post(api_url, json=payload)
            run_data = run_req.json()
            run_id = run_data["data"]["id"]
            dataset_id = run_data["data"]["defaultDatasetId"]
            
            # Polling for success
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
            for _ in range(15):
                check = requests.get(status_url).json()
                if check["data"]["status"] == "SUCCEEDED":
                    break
                await asyncio.sleep(5)
            
            res_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
            results = requests.get(res_url).json()
            
            if results and "downloadUrl" in results[0]:
                dl_link = results[0]["downloadUrl"]
                await status_msg.edit_text(f"✅ **Success!**\n\n🔗 [Download Now]({dl_link})", parse_mode="Markdown")
            else:
                await status_msg.edit_text("❌ Download link not found.")
        except Exception as e:
            await status_msg.edit_text(f"⚠️ Error: {str(e)}")
    else:
        await update.message.reply_text("❌ Send a valid Terabox link.")

def main():
    # Start web server thread
    Thread(target=run_web_server, daemon=True).start()
    
    # Initialize Application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Starting bot...")
    
    # Render-এর লুপ এরর এড়ানোর জন্য এটি সবথেকে নিরাপদ উপায়
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
