import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# توكن البوت الأساسي
BOT_TOKEN = "7947809298:AAGRitg_EtwO9oXuGlWo8vNLS8L07H9xqHw"

# معرف المشرف
ADMIN_ID = 1392151842

# توكن البوت الثاني (للتنبيه)
FORWARD_BOT_TOKEN = "7571959009:AAEMyaBvwTJVAQ5DR445HANtTAn6_xkWz3g"
FORWARD_CHAT_ID = 1392151842

def save_user(user_id, name):
    try:
        requests.post(f"https://api.telegram.org/bot{FORWARD_BOT_TOKEN}/sendMessage", json={
            "chat_id": FORWARD_CHAT_ID,
            "text": f"🆕 مستخدم جديد دخل البوت:\n\n👤 {name}\n🆔 {user_id}"
        })
    except Exception as e:
        print("User Notify Error:", e)

def get_tiktok_video(url):
    try:
        resolved = requests.head(url, allow_redirects=True).url
        res = requests.get("https://tikwm.com/api/", params={"url": resolved})
        data = res.json()
        return data["data"]["play"] if data.get("data") else None
    except Exception as e:
        print("TikTok Error:", e)
        return None

def get_youtube_video(url):
    try:
        video_id = ""
        if "youtube.com/watch?v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("/")[-1].split("?")[0]
        else:
            return None

        api_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
        res = requests.get(api_url)
        data = res.json()

        for stream in data.get("videoStreams", []):
            if stream["format"] == "mp4":
                return stream["url"]
        return None
    except Exception as e:
        print("YouTube Error:", e)
        return None

def get_instagram_video(url):
    try:
        api_url = "https://snapinsta.app/action.php?lang=en"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "url": url,
            "action": "post"
        }
        res = requests.post(api_url, headers=headers, data=data)
        html = res.text
        start = html.find('https://cdn')
        end = html.find('.mp4', start) + 4
        if start != -1 and end != -1:
            return html[start:end]
        return None
    except Exception as e:
        print("Instagram Error:", e)
        return None

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
        "❌ ما يطلب تشترك بقنوات\n"
        "❌ ما يعطيك روابط كذب ولا إعلانات\n"
        "✅ يدعم:\n🎵 تيك توك\n📸 إنستقرام\n▶️ يوتيوب\n✨ بدون علامة مائية\n\n"
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

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ البوت يعمل الآن...")
app.run_polling()