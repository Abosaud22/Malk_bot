import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import os

BOT_TOKEN = "7947809298:AAGRitg_EtwO9oXuGlWo8vNLS8L07H9xqHw"
ADMIN_ID = 1392151842
USERS_FILE = "users.json"
FORWARD_BOT_TOKEN = "7571959009:AAEMyaBvwTJVAQ5DR445HANtTAn6_xkWz3g"
FORWARD_CHAT_ID = 1392151842

def save_user(user_id, name):
    try:
        users = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        if str(user_id) not in users:
            users[str(user_id)] = name
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            requests.post(f"https://api.telegram.org/bot{FORWARD_BOT_TOKEN}/sendMessage", json={
                "chat_id": FORWARD_CHAT_ID,
                "text": f"🆕 مستخدم جديد دخل البوت:\n\n👤 {name}\n🆔 {user_id}"
            })
    except Exception as e:
        print("User Save Error:", e)

def get_tiktok_video(url):
    try:
        resolved = requests.head(url, allow_redirects=True).url
        res = requests.get("https://tikwm.com/api/", params={"url": resolved})
        data = res.json()
        return data["data"]["play"] if data.get("data") else None
    except Exception as e:
        print("TikTok Error:", e)
        return None

def get_video_by_yt_dlp(url):
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
        return f"ERROR: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.full_name)
    msg = (
        "ارحــبــوه🤝🏼\n\n"
        "بــوت تــحــمــيــل 📥\n\n"
        "المبرمج💻🇸🇦\n"
        "أبـو سـⓕ¹⁵ـعـود\n"
        "Snap: u_h0o\n"
        "Telegram: @lMIIIIIl\n\n"
        "مـمـيـزات الـبـوت 🤖\n\n"
        "❌ ما يطلب تشترك بقنوات\n"
        "❌ ما يعطيك روابط كذب ولا إعلانات\n\n"
        "✅ يدعم المواقع التالية:\n"
        "🎵 تيك توك\n"
        "📸 إنستقرام\n"
        "▶️ يوتيوب\n"
        "✨ وبدون علامة مائية\n\n"
        "📨 أرسل الرابط، وازهل الباقي 💪🏼"
    )
    await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    url = update.message.text.strip()
    video_url = None
    user = update.effective_user

    requests.post(f"https://api.telegram.org/bot{FORWARD_BOT_TOKEN}/sendMessage", json={
        "chat_id": FORWARD_CHAT_ID,
        "text": f"📩 المستخدم أرسل:\n\n👤 {user.full_name}\n🆔 {user.id}\n🔗 {url}"
    })

    if "tiktok.com" in url:
        video_url = get_tiktok_video(url)
    elif "instagram.com" in url or "instagr.am" in url:
        video_url = get_video_by_yt_dlp(url)
    elif "youtube.com" in url or "youtu.be" in url:
        video_url = get_video_by_yt_dlp(url)
    else:
        await update.message.reply_text("❌ الموقع غير مدعوم حالياً.")
        return

    if video_url and not video_url.startswith("ERROR:"):
        try:
            await update.message.reply_video(video=video_url)
        except:
            keyboard = [[InlineKeyboardButton("📥 تحميل الفيديو", url=video_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("اضغط الزر لتحميل الفيديو:", reply_markup=reply_markup)
    elif video_url and video_url.startswith("ERROR:"):
        await update.message.reply_text(f"⚠️ خطأ أثناء التحميل:\n{video_url}")
    else:
        await update.message.reply_text("⚠️ تعذر تحميل الفيديو. تأكد من الرابط أو جرب فيديو آخر.")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ هذا الأمر مخصص للمشرف فقط.")
        return
    if not os.path.exists(USERS_FILE):
        await update.message.reply_text("⚠️ لا يوجد مستخدمين حالياً.")
        return
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    msg = "📋 قائمة المستخدمين:\n\n"
    for idx, (uid, name) in enumerate(users.items(), 1):
        msg += f"{idx}. {name} - `{uid}`\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("users", list_users))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ البوت يعمل الآن...")
app.run_polling()