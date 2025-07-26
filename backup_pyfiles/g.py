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

TOKEN = "8492715732:AAGL_BYIzQUcbzlJ78kcUBHJM8USl5uVkIQ"

SONGS = {
    "mahnı 1": {
        "audio": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_700KB.mp3",
        "video": "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_480_1_5MG.mp4"
    },
    "mahnı 2": {
        "audio": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_1MG.mp3",
        "video": "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_640_3MG.mp4"
    },
    "mahnı 3": {
        "audio": "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_2MG.mp3",
        "video": "https://file-examples.com/wp-content/uploads/2017/04/file_example_MP4_1280_10MG.mp4"
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! Mahnı adı yaz, mən uyğun mahnıları göstərəcəm.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    results = [song for song in SONGS if query in song.lower()]
    if not results:
        await update.message.reply_text("Mahnı tapılmadı.")
        return
    keyboard = [
        [
            InlineKeyboardButton(f"{song} 🎵", callback_data=f"audio|{song}"),
            InlineKeyboardButton(f"{song} 🎥", callback_data=f"video|{song}")
        ] for song in results
    ]
    await update.message.reply_text("Tapılanlar:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    media_type, song = query.data.split("|")
    url = SONGS.get(song, {}).get(media_type)
    if not url:
        await query.message.reply_text("Bu format mövcud deyil.")
        return
    resp = requests.get(url)
    bio = io.BytesIO(resp.content)
    bio.name = f"{song}.{ 'mp3' if media_type=='audio' else 'mp4' }"
    if media_type == "audio":
        await query.message.reply_audio(audio=bio, title=song)
    else:
        await query.message.reply_video(video=bio, caption=song)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot işə düşdü...")
    app.run_polling()

if __name__ == "__main__":
    main()
