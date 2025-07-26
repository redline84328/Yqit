from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "8378651941:AAFNq1_NzTJdXH5ZCNnU4_Xyndgk94lr3Fs"

app = Client("fasonluYTBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_video_formats(url):
    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = {}
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get("height", 0)
                    if height in [480, 720, 1080] and f['ext'] == 'mp4':
                        formats[str(height)] = f['format_id']
            return formats
    except Exception as e:
        return str(e)

@app.on_message(filters.command("start"))
def welcome(_, msg):
    msg.reply(
        "👋 Salam! YouTube video və MP3 yükləmə botuna xoş gəldin.\n\n"
        "📥 Sadəcə YouTube linkini göndər və yükləmək istədiyin formatı seç.",
    )

@app.on_message(filters.text & filters.private)
def handle_link(_, msg):
    url = msg.text.strip()
    if not ("youtube.com" in url or "youtu.be" in url):
        return msg.reply("❌ Zəhmət olmasa düzgün bir YouTube linki göndər.")

    formats = get_video_formats(url)
    if isinstance(formats, str):
        return msg.reply(f"❌ Xəta baş verdi:\n`{formats}`")

    keyboard = [
        [InlineKeyboardButton("🎵 MP3 (Mahnı)", callback_data=f"mp3|{url}")],
    ]

    for quality in ["480", "720", "1080"]:
        if quality in formats:
            fmt_id = formats[quality]
            keyboard.append(
                [InlineKeyboardButton(f"📹 {quality}p Video", callback_data=f"video|{url}|{fmt_id}")]
            )

    msg.reply("📌 Format seçin:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query()
def download_file(_, query):
    data = query.data.split("|")
    action = data[0]
    url = data[1]
    msg = query.message

    if action == "mp3":
        status = msg.reply("🎶 MP3 yüklənir, zəhmət olmasa gözləyin...")
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'song.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status.edit_text("✅ MP3 yükləndi. Göndərilir...")
            query.message.reply_document("song.mp3", caption="🎵 Mahnın hazırdır.")
            os.remove("song.mp3")
        except Exception as e:
            status.edit_text(f"❌ Xəta baş verdi: `{e}`")

    elif action == "video":
        fmt_id = data[2]
        status = msg.reply("📹 Video yüklənir, zəhmət olmasa gözləyin...")
        try:
            ydl_opts = {
                'format': fmt_id,
                'outtmpl': 'video.%(ext)s',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            file_name = next((f for f in os.listdir() if f.startswith("video.")), None)
            status.edit_text("✅ Video yükləndi. Göndərilir...")
            query.message.reply_document(file_name, caption="🎬 Videon hazırdır.")
            os.remove(file_name)
        except Exception as e:
            status.edit_text(f"❌ Xəta baş verdi: `{e}`")

app.run()
