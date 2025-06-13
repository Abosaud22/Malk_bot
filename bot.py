import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# حماية
os.environ["PYTHONUNBUFFERED"] = "1"

BOT_TOKEN = "7947809298:AAGRitg_EtwO9oXuGlWo8vNLS8L07H9xqHw"
CHANNEL_ID = -1002525918633

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ارحــبــوه🤝🏼\n\n"
        "بــوت تــحــمــيــل 📥\n\n"
        "المبرمج💻🇸🇦\n"
        "أبـو سـⓕ¹⁵ـعـود\n"
        "Snap: u_h0o\n"
        "Telegram: @lMIIIIIl\n\n"
        "مـمـيـزات الـبـوت 🤖\n"
        "❌ ما يطلب تشترك بقنوات\n"
        "❌ ما يعطيك روابط كذب ولا إعلانات\n\n"
        "✅ يدعم:\n"
        "🎵 تيك توك (بدون علامة مائية)\n"
        "📸 إنستقرام\n"
        "▶️ يوتيوب\n\n"
        "📨 أرسل الرابط، وازهل الباقي 💪🏼"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "tiktok.com" in url:
        await handle_tiktok(update, context, url)

    elif "youtube.com" in url or "youtu.be" in url:
        await handle_youtube(update, context, url)

    elif "instagram.com" in url:
        await handle_instagram(update, context, url)

    else:
        await update.message.reply_text("❌ الرابط غير مدعوم. أرسل رابط من YouTube أو TikTok أو Instagram فقط.")

async def handle_youtube(update, context, url):
    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'best[ext=mp4]',
            'cookiefile': 'cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_path = "video.mp4"
        size = os.path.getsize(file_path)

        if size > 52428800:
            await update.message.reply_text("📤 الفيديو كبير، جاري رفعه على القناة...")
            msg = await context.bot.send_video(chat_id=CHANNEL_ID, video=open(file_path, 'rb'))
            link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg.message_id}"
            await update.message.reply_text(f"✅ تم الرفع:\n{link}")
        else:
            await update.message.reply_video(video=open(file_path, 'rb'))

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ أثناء تحميل اليوتيوب:\n{str(e)}")

async def handle_tiktok(update, context, url):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()

        if response.get("data") and response["data"].get("play"):
            video_url = response["data"]["play"]
            await update.message.reply_video(video=video_url, caption="🎵 TikTok تم التحميل بدون علامة مائية")
        else:
            await update.message.reply_text("❌ ما قدرنا نحمل الفيديو من TikTok. تأكد من الرابط.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ TikTok:\n{str(e)}")

async def handle_instagram(update, context, url):
    try:
        api_url = "https://igram.io/api/ajax"
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data = {"url": url}
        res = requests.post(api_url, headers=headers, data=data).json()

        if res.get("data") and res["data"].get("medias"):
            for media in res["data"]["medias"]:
                media_url = media.get("url")
                if media_url:
                    await update.message.reply_video(video=media_url, caption="📸 Instagram تحميل")
        else:
            await update.message.reply_text("❌ الرابط غير صالح أو خاص.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطأ Instagram:\n{str(e)}")

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()