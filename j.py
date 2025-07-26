import logging
import requests
import io
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8492715732:AAGL_BYIzQUcbzlJ78kcUBHJM8USl5uVkIQ"

# Mahnılar bazası (sınaq üçün statik fayllar)
SONGS = {
    "sevgi": {
        "title": "Sevgi Mahnısı",
        "mp3": "https://file-examples.com/storage/fe1f8be3f0f2e4025b2e424/2017/11/file_example_MP3_700KB.mp3",
        "mp4": "https://file-examples.com/storage/fe1f8be3f0f2e4025b2e424/2017/04/file_example_MP4_480_1_5MG.mp4"
    },
    "ayrılıq": {
        "title": "Ayrılıq Mahnısı",
        "mp3": "https://file-examples.com/storage/fe1f8be3f0f2e4025b2e424/2017/11/file_example_MP3_1MG.mp3",
        "mp4": "https://file-examples.com/storage/fe1f8be3f0f2e4025b2e424/2017/04/file_example_MP4_640_3MG.mp4"
    }
}

# Bot başladıqda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! Mahnı adı yaz (məsələn: sevgi) – sənə seçimlər təqdim edim 🎵🎥")

# Mahnı adı axtarılır
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    for key in SONGS:
        if key in text:
            song = SONGS[key]
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{key}"),
                 InlineKeyboardButton("🎥 MP4", callback_data=f"mp4|{key}")]
            ])
            await update.message.reply_text(f"{song['title']} üçün format seç:", reply_markup=keyboard)
            return
    await update.message.reply_text("😕 Üzr istəyirəm, uyğun mahnı tapılmadı.")

# Format seçiləndə MP3 və ya MP4 göndərilir
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    format, key = query.data.split("|")
    song = SONGS.get(key)

    if not song:
        await query.message.reply_text("Xəta: Mahnı tapılmadı.")
        return

    url = song.get(format)
    filename = f"{song['title']}.{format}"

    response = requests.get(url)
    file_data = io.BytesIO(response.content)
    file_data.name = filename

    if format == "mp3":
        await query.message.reply_audio(file_data, title=song['title'])
    else:
        await query.message.reply_video(file_data, caption=song['title'])

# Botu işə sal
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot başladı...")
    app.run_polling()

if __name__ == "__main__":
    main()
