import os
import requests
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.getenv("BOT_TOKEN")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_url = update.message.text
    if "terabox" in user_url or "nephobox" in user_url or "1024tera" in user_url:
        status_msg = await update.message.reply_text("⏳ Processing... please wait.")
        api_url = f"https://api.apify.com/v2/acts/easyapi~terabox-video-file-downloader/runs?token={APIFY_TOKEN}"
        payload = {"teraboxUrls": [user_url]}
        
        try:
            run_req = requests.post(api_url, json=payload).json()
            run_id = run_req["data"]["id"]
            dataset_id = run_req["data"]["defaultDatasetId"]
            
            # কাজ শেষ হওয়া পর্যন্ত অপেক্ষা (Polling)
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
            for _ in range(20): # সময় বাড়িয়ে ২০ বার করা হলো
                check = requests.get(status_url).json()
                if check["data"]["status"] == "SUCCEEDED":
                    break
                await asyncio.sleep(5)
            
            # রেজাল্ট ফেচ করা
            res_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
            results = requests.get(res_url).json()
            
            if results and len(results) > 0:
                item = results[0]
                # সব ধরণের সম্ভাব্য কি (Key) চেক করা হচ্ছে
                dl_link = item.get("downloadUrl") or item.get("download_link") or item.get("direct_link") or item.get("url")
                title = item.get("title") or item.get("fileName") or "Video File"
                
                if dl_link and str(dl_link).startswith("http"):
                    await status_msg.edit_text(f"✅ **Success!**\n\n📂 **Name:** {title}\n🔗 [Download Now]({dl_link})", parse_mode="Markdown")
                else:
                    await status_msg.edit_text("❌ API returned data but no download link found.")
            else:
                await status_msg.edit_text("❌ No data found in Apify dataset.")
                
        except Exception as e:
            await status_msg.edit_text(f"⚠️ Error: {str(e)}")
    else:
        await update.message.reply_text("❌ Please send a valid Terabox link.")

def main():
    Thread(target=run_web_server, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
