import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# توكن البوت
BOT_TOKEN = "7947809298:AAGRitg_EtwO9oXuGlWo8vNLS8L07H9xqHw"

# معرف القناة اللي يرفع فيها المقاطع الكبيرة
CHANNEL_ID = -1002525918633

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 أرسل رابط YouTube، وسأقوم بتحميله لك:\n\n"
        "✅ إذا كان صغيرًا سأرسله هنا\n"
        "📤 وإذا كان كبيرًا سأرفعه في قناة الأرشيف وأرجع لك الرابط."
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("❌ أرسل رابط من YouTube فقط.")
        return

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

        if size > 52428800:  # أكبر من 50MB
            await update.message.reply_text("📤 الفيديو كبير، جاري رفعه على القناة...")
            msg = await context.bot.send_video(chat_id=CHANNEL_ID, video=open(file_path, 'rb'))
            link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg.message_id}"
            await update.message.reply_text(f"✅ تم رفع الفيديو بنجاح:\n{link}")
        else:
            await update.message.reply_video(video=open(file_path, 'rb'))

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"⚠️ صار خطأ أثناء التحميل:\n\n{str(e)}")

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.run_polling()