import os
import re
import requests
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "7632674347:AAFsZlVP3iYQJ8UAXV8NCnj1KcMOCAI6Fj8"
ADMIN_ID = 1392151842
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
    elif "x.com" in url or "twitter.com" in url:
        return "twitter"
    return "unknown"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "ارحــبــوه 🤝🏼\n\n"
        "بــوت تــحــمــيــل 📥\n\n"
        "الـمـطـور 💻:\n"
        "أبـو سـⓕ¹⁵ـعـود 🇸🇦\n"
        "Snap: u_h0o\n"
        "Telegram: @lMIIIIIl\n\n"
        "مــمــيـزات:\n"
        "📽 فـيـديـو\n"
        "🔉 صـــوت\n\n"
        "✅ يدعم:\n"
        "🎵 تيك توك\n"
        "📸 إنستقرام\n"
        "▶️ يوتيوب\n"
        "🐦 تويتر\n\n"
        "⛔️ بدون قنوات ولا وجع راس\n"
        "📨 أرسل الرابط، وازهل الباقي 💪🏼"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 مستخدم جديد دخل البوت:\n\n"
             f"👤 الاسم: {user.full_name}\n"
             f"🆔 المعرف: {user.id}\n"
             f"📛 اليوزر: @{user.username if user.username else 'لا يوجد'}"
    )

async def ask_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = clean_url(update.message.text.strip())
    platform = get_platform(url)
    user = update.effective_user

    # تنبيه للمطوّر
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 رسالة جديدة:\n\n"
             f"👤 الاسم: {user.full_name}\n"
             f"🆔 المعرف: {user.id}\n"
             f"📛 اليوزر: @{user.username if user.username else 'لا يوجد'}\n\n"
             f"📎 أرسل: {url}"
    )

    if platform == "unknown":
        await update.message.reply_text("❌ الرابط غير مدعوم.")
        return

    URL_STORE[user.id] = (url, platform)

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
            'format': 'bestaudio/best' if choice == "audio" else 'bestvideo+bestaudio/best',
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
            ext = "mp3" if choice == "audio" else info.get("ext", "mp4")
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

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await context.bot.send_message(chat_id=user_id, text=f"⚠️ خطأ:\n{str(e)}")

async def handle_tiktok(context, user_id, url, choice):
    try:
        res = requests.get(f"https://tikwm.com/api/?url={url}").json()
        if not res.get("success", False):
            await context.bot.send_message(chat_id=user_id, text="❌ تعذر تحميل الفيديو من تيك توك.")
            return

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

# أمر رد من المطوّر لأي مستخدم
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        args = context.args
        target_id = int(args[0])
        message = ' '.join(args[1:])
        await context.bot.send_message(chat_id=target_id, text=message)
        await update.message.reply_text("✅ تم إرسال الرد.")
    except:
        await update.message.reply_text("❌ الصيغة: /رد [id] [رسالتك]")

# تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("رد", admin_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_format))
app.add_handler(CallbackQueryHandler(handle_choice))
app.run_polling()