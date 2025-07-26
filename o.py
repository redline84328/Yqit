from pyrogram import Client, filters
from pytube import YouTube
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import os

API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "8492715732:AAGL_BYIzQUcbzlJ78kcUBHJM8USl5uVkIQ"

app = Client("yt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Başlanğıc mesajı
@app.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("🔗 YouTube link göndər, sənə MP3 və MP4 seçimləri təqdim edim.")

# Link gələndə
@app.on_message(filters.regex(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/\S+'))
async def yt_menu(_, msg: Message):
    url = msg.text
    try:
        yt = YouTube(url)
        title = yt.title

        buttons = [
            [InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{url}")],
            [InlineKeyboardButton("📹 360p", callback_data=f"360|{url}"),
             InlineKeyboardButton("720p", callback_data=f"720|{url}"),
             InlineKeyboardButton("1080p", callback_data=f"1080|{url}")]
        ]
        await msg.reply(f"🎬 *{title}*\nFormat seç:", reply_markup=InlineKeyboardMarkup(buttons), quote=True)
    except:
        await msg.reply("❌ Xəta baş verdi. Düzgün YouTube linki göndər.")

# Format seçiləndə
@app.on_callback_query()
async def send_media(_, query):
    await query.answer()
    format_type, url = query.data.split("|")
    yt = YouTube(url)
    title = yt.title.replace(" ", "_")
    file_path = ""

    if format_type == "mp3":
        stream = yt.streams.filter(only_audio=True).first()
        file_path = f"{title}.mp4"
        stream.download(filename=file_path)
        out_file = f"{title}.mp3"
        os.system(f"ffmpeg -i '{file_path}' -vn -ab 128k -ar 44100 -y '{out_file}'")
        await query.message.reply_audio(audio=out_file, title=yt.title)
        os.remove(file_path)
        os.remove(out_file)

    else:
        stream = yt.streams.filter(res=f"{format_type}p", file_extension="mp4", progressive=True).first()
        if not stream:
            await query.message.reply(f"❌ {format_type}p formatı mövcud deyil.")
            return
        file_path = f"{title}_{format_type}p.mp4"
        stream.download(filename=file_path)
        await query.message.reply_video(video=file_path, caption=yt.title)
        os.remove(file_path)

if __name__ == "__main__":
    print("✅ Bot işə düşdü...")
    app.run()
