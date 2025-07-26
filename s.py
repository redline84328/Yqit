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

# Hardkod mahnı bazası: mahnı adı -> {"audio": mp3_url, "video": mp4_url}
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

# Step 1: İstifadəçidən mahnı soruşuruq
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salam! Mahnı adı və ya söz yaz, mən uyğun mahnıları təqdim edim."
    )

# Step 2: Axtarış və uyğun mahnıların inline düymələrini göstəririk
async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().lower()
    found_songs = [song for song in SONGS if query in song.lower()]

    if not found_songs:
        await update.message.reply_text("Üzr istəyirəm, mahnı tapılmadı.")
        return

    keyboard = []
    for song in found_songs:
        # Hər mahnı üçün iki düymə: Audio və Video
        buttons = [
            InlineKeyboardButton(text=f"{song} 🎵 Audio", callback_data=f"audio|{song}"),
            InlineKeyboardButton(text=f"{song} 🎥 Video", callback_data=f"video|{song}"),
        ]
        keyboard.append(buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Tapılan mahnılar:", reply_markup=reply_markup)

# Step 3: Callback query-də audio ya video göndəririk
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # format: "audio|mahnı 1" və ya "video|mahnı 2"
    media_type, song_name = data.split("|", maxsplit=1)

    song_info = SONGS.get(song_name)

    if not song_info:
        await query.message.reply_text("Bu mahnı mövcud deyil.")
        return

    url = song_info.get(media_type)
    if not url:
        await query.message.reply_text(f"{media_type.title()} versiyası mövcud deyil.")
        return

    try:
        resp = requests.get(url)
        resp.raise_for_status()
        media_bytes = io.BytesIO(resp.content)
        ext = "mp3" if media_type == "audio" else "mp4"
        media_bytes.name = f"{song_name}.{ext}"

        if media_type == "audio":
            await query.message.reply_audio(audio=media_bytes, title=song_name)
        else:
            await query.message.reply_video(video=media_bytes, caption=song_name)

    except Exception as e:
        await query.message.reply_text(f"{media_type.title()} yüklənərkən xəta baş verdi.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_song))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot işləyir...")
    application.run_polling()

if __name__ == "__main__":
    main()
