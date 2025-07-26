from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "7919152602:AAGG-OYTj_YUm6f42nvtT5uoCg-FcL9IkQI"

# Hardkod nümunə mahnılar
SONGS = {
    "mahnı 1": "https://example.com/song1.mp3",
    "mahnı 2": "https://example.com/song2.mp3",
    "mahnı 3": "https://example.com/song3.mp3",
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
        await query.message.reply_text(f"\"{song_name}\" mahnısının yükləmə linki:\n{song_url}")
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
