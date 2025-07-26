from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pytube import YouTube
import os

# --- API məlumatları (sənin verdiyin)
API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "8116239967:AAEUXR7rWMAqQxKhdms2wVPF85jNq9H-EY8"

# --- Pyrogram botu yaradılır
app = Client("youtube_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# --- Endirmə qovluğu yaradılır
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# --- Keçici yaddaş (linkləri saxlayırıq)
link_cache = {}

# --- YouTube keyfiyyətlərini alır
def get_stream_options(url):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()
    audio = yt.streams.filter(only_audio=True).first()
    options = {f"{s.resolution} - {s.fps}fps": s.itag for s in streams}
    if audio:
        options["MP3 - Audio Only"] = audio.itag
    return yt.title, options

# --- /start komandası
@app.on_message(filters.command("start"))
def start(_, msg):
    msg.reply("🔗 Sadəcə YouTube linkini göndər və yükləmək üçün keyfiyyət seç!")

# --- YouTube linki gəldikdə
@app.on_message(filters.text & filters.private)
def download_handler(_, msg):
    url = msg.text.strip()
    if not url.startswith("http"):
        msg.reply("❌ Zəhmət olmasa keçərli bir YouTube linki göndərin.")
        return

    try:
        yt = YouTube(url)
        title, options = get_stream_options(url)
        link_cache[str(msg.chat.id)] = url  # Linki yadda saxla

        buttons = [
            [InlineKeyboardButton(text=opt, callback_data=itag)]
            for opt, itag in options.items()
        ]
        msg.reply(
            f"🎬 *{title}*\n\n📥 Aşağıdakı keyfiyyəti seç:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="markdown"
        )
    except Exception as e:
        msg.reply(f"⚠️ Xəta baş verdi: {e}")

# --- Seçim etdikdə (MP3 və ya Video)
@app.on_callback_query()
def callback_handler(_, query: CallbackQuery):
    chat_id = str(query.message.chat.id)
    if chat_id not in link_cache:
        query.message.edit("❌ Əlaqəli link tapılmadı.")
        return

    url = link_cache[chat_id]
    itag = int(query.data)
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)
    is_audio = "audio" in stream.mime_type

    msg = query.message.reply("⏬ Yüklənir, zəhmət olmasa gözləyin...")

    try:
        out_file = stream.download(output_path=DOWNLOAD_FOLDER)
        if is_audio:
            mp3_file = out_file.replace(".mp4", ".mp3")
            os.system(f"ffmpeg -i '{out_file}' -vn -ab 192k -ar 44100 -y '{mp3_file}'")
            os.remove(out_file)
            query.message.reply_document(mp3_file, caption="🎧 MP3 yükləndi.")
            os.remove(mp3_file)
        else:
            query.message.reply_video(out_file, caption="🎬 Video yükləndi.")
            os.remove(out_file)

        msg.delete()
    except Exception as e:
        msg.edit(f"❌ Xəta baş verdi: {e}")

# --- Botu işə sal
app.run()
