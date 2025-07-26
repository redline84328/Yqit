import os
from pytube import YouTube
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

BOT_TOKEN = "8118875124:AAENf_UOqo34Xg9wXLhYy6vHEej6DsNZJc0"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Salam! YouTube linkini göndər, video və ya MP3 kimi yükləyək.")

def is_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url

def get_options(url):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()
    audio = yt.streams.filter(only_audio=True).first()
    options = {f"{s.resolution} - {s.fps}fps": s.itag for s in streams}
    if audio:
        options["🎵 MP3 - Audio Only"] = audio.itag
    return yt.title, options

def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    if not is_youtube_url(url):
        update.message.reply_text("❌ Düzgün YouTube linki göndər.")
        return
    try:
        title, options = get_options(url)
        keyboard = [
            [InlineKeyboardButton(text=label, callback_data=str(itag))]
            for label, itag in options.items()
        ]
        context.user_data["url"] = url
        update.message.reply_text(
            f"🎬 *{title}*\n\nAşağıdakı keyfiyyətdən birini seç:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        update.message.reply_text(f"Xəta baş verdi: {e}")

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    url = context.user_data.get("url")
    if not url:
        query.edit_message_text("❌ Link tapılmadı.")
        return
    itag = int(query.data)
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        is_audio = "audio" in stream.mime_type

        query.edit_message_text("Yüklənir, gözlə...")

        file_path = stream.download(output_path=DOWNLOAD_DIR)
        if is_audio:
            mp3_path = file_path.replace(".mp4", ".mp3")
            os.system(f"ffmpeg -i '{file_path}' -vn -ab 192k -ar 44100 -y '{mp3_path}'")
            os.remove(file_path)
            query.message.reply_document(open(mp3_path, 'rb'), caption="🎧 MP3 yükləndi.")
            os.remove(mp3_path)
        else:
            query.message.reply_video(open(file_path, 'rb'), caption="🎬 Video yükləndi.")
            os.remove(file_path)
    except Exception as e:
        query.edit_message_text(f"Yükləmə zamanı xəta: {e}")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
