import os
import asyncio
from pytube import YouTube
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8118875124:AAENf_UOqo34Xg9wXLhYy6vHEej6DsNZJc0"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! YouTube linkini göndər və video və ya MP3 kimi yüklə.")

def is_youtube_url(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def get_options(url):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()
    audio = yt.streams.filter(only_audio=True).first()
    options = {f"{s.resolution} - {s.fps}fps": s.itag for s in streams}
    if audio:
        options["🎵 MP3 - Audio Only"] = audio.itag
    return yt.title, options

async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, stream, is_audio):
    query = update.callback_query
    await query.edit_message_text("Yüklənir, gözlə...")

    def download():
        return stream.download(output_path=DOWNLOAD_DIR)

    file_path = await asyncio.to_thread(download)

    if is_audio:
        mp3_path = file_path.replace(".mp4", ".mp3")
        cmd = f"ffmpeg -i '{file_path}' -vn -ab 192k -ar 44100 -y '{mp3_path}'"
        await asyncio.to_thread(os.system, cmd)
        os.remove(file_path)
        with open(mp3_path, 'rb') as f:
            await query.message.reply_document(f, caption="🎧 MP3 yükləndi.")
        os.remove(mp3_path)
    else:
        with open(file_path, 'rb') as f:
            await query.message.reply_video(f, caption="🎬 Video yükləndi.")
        os.remove(file_path)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not is_youtube_url(url):
        await update.message.reply_text("❌ Düzgün YouTube linki göndər.")
        return
    try:
        title, options = get_options(url)
        keyboard = [
            [InlineKeyboardButton(text=label, callback_data=str(itag))]
            for label, itag in options.items()
        ]
        context.user_data["url"] = url
        await update.message.reply_text(
            f"🎬 *{title}*\n\nAşağıdakı keyfiyyətdən birini seç:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("❌ Link tapılmadı.")
        return
    itag = int(query.data)
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        is_audio = "audio" in stream.mime_type
        await download_and_send(update, context, stream, is_audio)
    except Exception as e:
        await query.edit_message_text(f"Yükləmə zamanı xəta: {e}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
