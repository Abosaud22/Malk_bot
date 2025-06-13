import os
import re
import requests
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# إعدادات عامة
BOT_TOKEN = "7947809298:AAGRitg_EtwO9oXuGlWo8vNLS8L07H9xqHw"
CHANNEL_ID = -1002525918633
URL_STORE = {}

def clean_url(url):
    return url.split("?")[0]

def get_platform(url):
    if "tiktok.com" in url:
        return "tiktok"
    elif "instagram.com" in url or "instagr.am" in url:
        return "instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "unknown"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ارحــبــوه🤝🏼\n\n"
        "بــوت تــحــمــيــل 📥\n\n"
        "المبرمج💻🇸🇦 أبـو سـⓕ¹⁵ـعـود\n"
        "Snap: u_h0o\nTelegram: @lMIIIIIl\n\n"
        "✅ يدعم:\n🎵 تيك توك\n📸 إنستقرام\n▶️ يوتيوب\n\n"
        "📨 أرسل الرابط، وازهل الباقي 💪🏼"
    )

async def ask_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = clean_url(update.message.text.strip())
    platform = get_platform(url)
    if platform == "unknown":
        await update.message.reply_text("❌ الرابط غير مدعوم.")
        return

    URL_STORE[update.effective_user.id] = (url, platform)

    keyboard = [[
        InlineKeyboardButton("🎥 فيديو", callback_data="video"),
        InlineKeyboardButton("🎧 صوت", callback_data="audio")
    ]]
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    user_id = query.from_user.id

    if user_id not in URL_STORE:
        await query.edit_message_text("❌ لم يتم العثور على الرابط.")
        return

    url, platform = URL_STORE[user_id]
    await query.edit_message_text("⏳ جاري التحميل...")

    if platform == "tiktok":
        await handle_tiktok(context, user_id, url, choice)
    else:
        await handle_with_ytdlp(context, user_id, url, choice)

async def handle_with_ytdlp(context, user_id, url, choice):
    try:
        filename = f"file_{user_id}"
        ydl_opts = {
            'outtmpl': f'{filename}.%(ext)s',
            'format': 'bestaudio/best' if choice == "audio" else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'cookiefile': 'cookies_instagram.txt' if "instagram.com" in url else 'cookies.txt',
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

        if size > 52428800:
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

async def handle_tiktok(context, user_id, url, choice):
    try:
        res = requests.get(f"https://tikwm.com/api/?url={url}").json()
        data = res.get("data", {})

        if choice == "audio":
            audio_url = data.get("music")
            if not audio_url:
                await context.bot.send_message(chat_id=user_id, text="❌ ما حصلنا الصوت.")
                return
            await context.bot.send_audio(chat_id=user_id, audio=audio_url)
        else:
            video_url = data.get("play")
            if not video_url:
                await context.bot.send_message(chat_id=user_id, text="❌ ما حصلنا الفيديو.")
                return
            await context.bot.send_video(chat_id=user_id, video=video_url)

    except Exception as e:
        await context.bot.send_message(chat_id=user_id, text=f"⚠️ خطأ TikTok:\n{str(e)}")

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_format))
app.add_handler(CallbackQueryHandler(handle_choice))
app.run_polling()