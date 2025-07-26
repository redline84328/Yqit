from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import requests
import io

TOKEN = "7919152602:AAGG-OYTj_YUm6f42nvtT5uoCg-FcL9IkQI"

# Mahnı siyahısı: ad -> mp3 URL
SONGS = {
    "Mahnı 1": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_700KB.mp3",
    "Mahnı 2": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_1MG.mp3",
    "Mahnı 3": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_2MG.mp3",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salam! Mənə mahnı adı və ya mahnı sözləri yaz, sənə seçimləri təqdim edəcəm."
    )

async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().lower()

    # İstifadəçi nə yazırsa yazsın, bütün mahnıları göstəririk
    keyboard = [
        [InlineKeyboardButton(text=song, callback_data=song)]
        for song in SONGS
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"\"{query}\" üçün tapılan mahnılar:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    song_name = query.data
    song_url = SONGS.get(song_name)

    if song_url:
        try:
            resp = requests.get(song_url)
            resp.raise_for_status()
            audio_bytes = io.BytesIO(resp.content)
            audio_bytes.name = f"{song_name}.mp3"
            await query.message.reply_audio(audio=audio_bytes, title=song_name)
        except Exception as e:
            await query.message.reply_text("Mahnını yükləmək mümkün olmadı.")
    else:
        await query.message.reply_text("Bu mahnı mövcud deyil.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_song))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot işləyir...")
    application.run_polling()

if __name__ == "__main__":
    main()
