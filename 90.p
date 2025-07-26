
import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# 🔐 Telegram Bot Tokeni
TOKEN = "8047562257:AAFxBckzVrX3O3XiU0TaXM2EE6KqgeTGzhk"

# 💾 Keçici yaddaş
user_links = {}

# 🎬 Format menyusu
format_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎵 MP3 (səs)", callback_data="mp3")],
    [InlineKeyboardButton("📹 MP4 360p", callback_data="360"),
     InlineKeyboardButton("MP4 480p", callback_data="480")],
    [InlineKeyboardButton("MP4 720p", callback_data="720"),
     InlineKeyboardButton("MP4 1080p", callback_data="1080")]
])

# 🟢 Start komandası
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎧 YouTube link göndərin və formatı seçin:")

# 🔗 Linki qəbul et
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "youtube.com" in text or "youtu.be" in text:
        user_links[update.effective_user.id] = text
        await update.message.reply_text("📥 Format seçin:", reply_markup=format_menu)
    else:
        await update.message.reply_text("❌ Zəhmət olmasa keçərli YouTube linki göndərin.")

# 📦 Yükləmə və göndərmə
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    format_choice = query.data

    if user_id not in user_links:
        await query.edit_message_text("❌ Əvvəlcə YouTube linki göndərin.")
        return

    url = user_links[user_id]
    await query.edit_message_text("⏬ Yüklənir, zəhmət olmasa gözləyin...")

    try:
        # Məlumat almaq üçün
        info = yt_dlp.YoutubeDL().extract_info(url, download=False)
        title = info.get("title", "video")
        safe_title = "".join(i for i in title if i.isalnum() or i in " _-").strip()
        filename = f"{safe_title}.{'mp3' if format_choice == 'mp3' else 'mp4'}"

        # Yükləmə ayarları
        if format_choice == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': filename,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
                'prefer_ffmpeg': True,
                'quiet': True,
            }
        else:
            ydl_opts = {
                'format': f'bestvideo[height<={format_choice}]+bestaudio/best',
                'outtmpl': filename,
                'merge_output_format': 'mp4',
                'prefer_ffmpeg': True,
                'quiet': True,
            }

        # Yükləmə
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Göndər
        await context.bot.send_document(chat_id=query.message.chat_id, document=open(filename, "rb"))
        os.remove(filename)

    except Exception as e:
        await query.edit_message_text(f"⚠️ Xəta baş verdi:\n{e}")

# ▶️ Botu işə sal
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot hazırdır.")
    app.run_polling()
