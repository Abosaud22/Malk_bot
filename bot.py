
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import os

# 🔑 التوكن من متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------- TikTok --------
def get_tiktok_video(url):
    try:
        resolved = requests.head(url, allow_redirects=True).url
        res = requests.get("https://tikwm.com/api/", params={"url": resolved})
        data = res.json()
        return data["data"]["play"] if data.get("data") else None
    except Exception as e:
        print("TikTok Error:", e)
        return None

# -------- Instagram (yt_dlp) --------
def get_instagram_video(url):
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url']
    except Exception as e:
        print("Instagram Error:", e)
        return None

# -------- YouTube (yt_dlp) --------
def get_youtube_video(url):
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url']
    except Exception as e:
        print("YouTube Error:", e)
        return None

# -------- Telegram Bot --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 أرسل رابط TikTok أو Instagram أو YouTube وسأرسل لك زر لتحميله بدون علامة مائية!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    video_url = None

    if "tiktok.com" in url:
        video_url = get_tiktok_video(url)
    elif "instagram.com" in url:
        video_url = get_instagram_video(url)
    elif "youtube.com" in url or "youtu.be" in url:
        video_url = get_youtube_video(url)
    else:
        await update.message.reply_text("❌ الموقع غير مدعوم حالياً.")
        return

    if video_url:
        try:
            await update.message.reply_video(video=video_url)
        except:
            keyboard = [[InlineKeyboardButton("📥 تحميل الفيديو", url=video_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("اضغط الزر لتحميل الفيديو:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("⚠️ تعذر تحميل الفيديو. تأكد من الرابط أو جرب فيديو آخر.")

# -------- تشغيل البوت --------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("✅ البوت يعمل الآن...")
app.run_polling()
