import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# 🔐 Telegram Bot Tokeni buraya yazılıb:
TOKEN = "8229286771:AAElPDPkrRU1BzRRZ8Oz8Kbh9mPqHYtYxMk"

# ✅ Keyfiyyət seçimləri
quality_options = [
    ("MP3 (128kbps)", "mp3"),
    ("360p", "360"),
    ("480p", "480"),
    ("720p", "720"),
    ("1080p", "1080")
]

user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 YouTube link göndərin və formatı seçin.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        user_links[update.effective_user.id] = url
        keyboard = [[InlineKeyboardButton(text, callback_data=code)] for text, code in quality_options]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📥 Format seçin:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ Zəhmət olmasa keçərli YouTube linki göndərin.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_links:
        await query.edit_message_text("❌ Əvvəlcə video linki göndərin.")
        return

    url = user_links[user_id]
    choice = query.data
    output_name = f"{user_id}_{choice}.%(ext)s"
    ydl_opts = {}

    if choice == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'prefer_ffmpeg': True,
            'quiet': True,
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={choice}]+bestaudio/best',
            'outtmpl': output_name,
            'merge_output_format': 'mp4',
            'prefer_ffmpeg': True,
            'quiet': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == "mp3":
                filename = filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")

        await query.edit_message_text("✅ Yükləndi, göndərilir...")
        await context.bot.send_document(chat_id=query.message.chat_id, document=open(filename, "rb"))
        os.remove(filename)

    except Exception as e:
        await query.edit_message_text(f"⚠️ Xəta baş verdi:\n{e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot işə düşdü!")
    app.run_polling()
