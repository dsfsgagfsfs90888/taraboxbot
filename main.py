import os
import time
import requests
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Flask setup for Render
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Tokens from Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text
    if "terabox" in user_url or "nephobox" in user_url:
        status_msg = await update.message.reply_text("⏳ Processing Terabox link... please wait.")
        api_url = f"https://api.apify.com/v2/acts/easyapi~terabox-video-file-downloader/runs?token={APIFY_TOKEN}"
        payload = {"teraboxUrls": [user_url]}
        try:
            run_req = requests.post(api_url, json=payload)
            run_data = run_req.json()
            run_id = run_data["data"]["id"]
            dataset_id = run_data["data"]["defaultDatasetId"]
            
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
            for _ in range(15):
                check = requests.get(status_url).json()
                if check["data"]["status"] == "SUCCEEDED":
                    break
                await asyncio.sleep(5)
            
            results = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}").json()
            if results and "downloadUrl" in results[0]:
                dl_link = results[0]["downloadUrl"]
                await status_msg.edit_text(f"✅ **File Ready!**\n\n🔗 [Download Now]({dl_link})", parse_mode="Markdown")
            else:
                await status_msg.edit_text("❌ Link extraction failed.")
        except Exception as e:
            await status_msg.edit_text(f"⚠️ Error: {str(e)}")
    else:
        await update.message.reply_text("❌ Send a valid Terabox link.")

def main():
    # Start web server thread
    Thread(target=run_web_server, daemon=True).start()

    # Build the application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting...")
    # This is the correct way to run in current versions
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
            
            run_id = run_data["data"]["id"]
            dataset_id = run_data["data"]["defaultDatasetId"]
            
            # Polling for completion (Checking every 5 seconds)
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
            for _ in range(12): # Max 1 minute wait
                check = requests.get(status_url).json()
                if check["data"]["status"] == "SUCCEEDED":
                    break
                await asyncio.sleep(5)
            
            # Fetch the result
            results = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}").json()
            
            if results and "downloadUrl" in results[0]:
                dl_link = results[0]["downloadUrl"]
                file_name = results[0].get("title", "Video File")
                await status_msg.edit_text(f"✅ **File Ready!**\n\n📂 **Name:** {file_name}\n🔗 [Download Now]({dl_link})", parse_mode="Markdown")
            else:
                await status_msg.edit_text("❌ Link extraction failed. Try another link.")
                
        except Exception as e:
            await status_msg.edit_text(f"⚠️ API Error: {str(e)}")
    else:
        await update.message.reply_text("❌ Please send a valid Terabox or Nephobox link.")

def main():
    # Start web server thread
    Thread(target=run_web_server, daemon=True).start()

    # Start Bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
