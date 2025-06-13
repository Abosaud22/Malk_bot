import os
import re
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# حماية
os.environ["PYTHONUNBUFFERED"] = "1"

BOT_TOKEN = "7947809298:AAGRitg_EtwO9oXuGlWo8vNLS8L07H9xqHw"
CHANNEL_ID = -1002525918633
URL_STORE = {}  # لتخزين الرابط مؤقتًا

def clean_url(url):
    return url.split("?")[0]

def is_supported_url(url):
    return any(x in url for x in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "instagr.am"])

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
        "🎵 تيك توك\n"
        "📸 إنستقرام\n"
        "▶️ يوتيوب\n\n"
        "📨 أرسل الرابط، وازهل الباقي 💪🏼"
    )

async def ask_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = clean_url(update.message.text.strip())
    if not is_supported_url(url):
        await update.message.reply_text("❌ الرابط غير مدعوم.")
        return

    user_id = update.effective_user.id
    URL_STORE[user_id] = url

    keyboard = [
        [InlineKeyboardButton("🎥 تحميل فيديو", callback_data="video"),
         InlineKeyboardButton("🎧 تحميل صوت", callback_data="audio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر التنسيق:", reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    user_id = query.from_user.id

    url = URL_STORE.get(user_id)
    if not url:
        await query.edit_message_text("❌ لم يتم العثور على رابط. أرسل الرابط من جديد.")
        return

    await query.edit_message_text("⏳ جاري التحميل...")

    try:
        filename = f"file_{user_id}"
        ydl_opts = {
            'outtmpl': f'{filename}.%(ext)s',
            'format': 'bestaudio/best' if choice == "audio" else 'bestvideo+bestaudio/best',
            'cookiefile': 'cookies.txt',
            'postprocessors': []
        }

        if choice == "audio":
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = "mp3" if choice == "audio" else info['ext']
            file_path = f"{filename}.{ext}"

        size = os.path.getsize(file_path)

        if size > 52428800:  # أكبر من 50MB
            msg = await context.bot.send_document(chat_id=CHANNEL_ID, document=open(file_path, 'rb'))
            link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg.message_id}"
            await context.bot.send_message(chat_id=user_id, text=link)
        else:
            if choice == "audio":
                await context.bot.send_audio(chat_id=user_id, audio=open(file_path, 'rb'))
            else:
                await context.bot.send_video(chat_id=user_id, video=open(file_path, 'rb'))

        os.remove(file_path)

    except Exception as e:
        await context.bot.send_message(chat_id=user_id, text=f"⚠️ خطأ:\n{str(e)}")

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_format))
app.add_handler(CallbackQueryHandler(handle_choice))
app.run_polling()