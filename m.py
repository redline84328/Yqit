from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import io
import requests

TOKEN = "7919152602:AAGG-OYTj_YUm6f42nvtT5uoCg-FcL9IkQI"

# Nümunə mahnılar (mp3 URL-ləri real olmalıdır)
SONGS = {
    "mahnı 1": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_700KB.mp3",
    "mahnı 2": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_1MG.mp3",
    "mahnı 3": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_2MG.mp3",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salam! Mahnı adı və ya söz yaz, mən sənə mahnı variantları təqdim edim."
    )

async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower().strip()

    found_songs = [song for song in SONGS if query in song.lower()]

    if not found_songs:
        await update.message.reply_text("Üzr istəyirəm, mahnı tapılmadı.")
        return

    keyboard = [
        [InlineKeyboardButton(text=song, callback_data=song)]
        for song in found_songs
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
        # MP3 faylını yüklə
        resp = requests.get(song_url)
        if resp.status_code == 200:
            audio_bytes = io.BytesIO(resp.content)
            audio_bytes.name = f"{song_name}.mp3"

            # Telegram-da audio olaraq göndər
            await query.message.reply_audio(audio=audio_bytes, title=song_name)
        else:
            await query.message.reply_text("Mahnını yükləmək mümkün olmadı.")
    else:
        await query.message.reply_text("Üzr istəyirəm, bu mahnı haqqında məlumat yoxdur.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_song))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot işləyir...")
    application.run_polling()

if __name__ == "__main__":
    main()
