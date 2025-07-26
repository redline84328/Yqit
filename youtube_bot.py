from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytube import YouTube
import os
import uuid

API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "8116239967:AAEUXR7rWMAqQxKhdms2wVPF85jNq9H-EY8"

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# UUID əsaslı yaddaş (çəkinmədən çox link saxlaya bilərik)
link_cache = {}

def get_options(url):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()
    audio = yt.streams.filter(only_audio=True).first()
    options = {f"{s.resolution} - {s.fps}fps": s.itag for s in streams}
    if audio:
        options["🎵 MP3 - Audio Only"] = audio.itag
    return yt.title, options

@app.on_message(filters.command("start"))
def welcome(_, message):
    message.reply("👋 Salam! Sadəcə YouTube linkini göndər, video və ya MP3 şəklində yüklə!")

@app.on_message(filters.private & filters.text)
def handle_url(_, message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        message.reply("❌ Zəhmət olmasa keçərli bir YouTube linki göndərin.")
        return
    try:
        title, options = get_options(url)
        key = str(uuid.uuid4())
        link_cache[key] = url
        buttons = [
            [InlineKeyboardButton(text=label, callback_data=f"{key}|{itag}")]
            for label, itag in options.items()
        ]
        message.reply(
            f"🎬 *{title}*\n\n📥 Aşağıdan format və keyfiyyəti seç:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="markdown"
        )
    except Exception as e:
        message.reply(f"⚠️ Xəta baş verdi: {e}")

@app.on_callback_query()
def process_choice(_, query: CallbackQuery):
    try:
        data = query.data.split("|")
        key, itag = data[0], int(data[1])
        url = link_cache.get(key)
        if not url:
            query.message.edit("⛔ Link tapılmadı və ya vaxtı keçib.")
            return
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        is_audio = "audio" in stream.mime_type
        msg = query.message.reply("🔄 Yüklənir...")

        file_path = stream.download(output_path=DOWNLOAD_DIR)
        if is_audio:
            mp3_file = file_path.replace(".mp4", ".mp3")
            os.system(f"ffmpeg -i '{file_path}' -vn -ab 192k -ar 44100 -y '{mp3_file}'")
            os.remove(file_path)
            query.message.reply_document(mp3_file, caption="🎧 MP3 yükləndi.")
            os.remove(mp3_file)
        else:
            query.message.reply_video(file_path, caption="🎬 Video yükləndi.")
            os.remove(file_path)

        msg.delete()
    except Exception as e:
        query.message.reply(f"❌ Yükləmə zamanı xəta: {e}")

app.run()
