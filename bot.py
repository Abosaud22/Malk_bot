import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# توكن البوت
BOT_TOKEN = "7947809298:AAGRitg_EtwO9oXuGlWo8vNLS8L07H9xqHw"

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 أرسل رابط YouTube لتحميله.\n"
        "✅ يدعم المقاطع المحمية باستخدام cookies.txt\n"
        "⚠️ الحد الأقصى للحجم هو 50MB بسبب قيود تيليجرام."
    )

# تحميل الفيديو
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("❌ هذا الرابط غير مدعوم. أرسل رابط من YouTube فقط.")
        return

    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'best[ext=mp4]',
            'cookiefile': 'cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_video(video=open("video.mp4", 'rb'))
        os.remove("video.mp4")

    except Exception as e:
        await update.message.reply_text(f"⚠️ صار خطأ أثناء التحميل:\n\n{str(e)}")

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
app.run_polling()