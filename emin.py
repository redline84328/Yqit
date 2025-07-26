from pyrogram import Client, filters
import yt_dlp
import requests
import re
import os

API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "7971690119:AAHFfd4lD5LBw-bFI0SQbQ2_6YwdIbexg9E"

app = Client("spotify_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# YouTube-dan MP3 yükləmək
def download_mp3(search_query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search_query}", download=True)
        filename = ydl.prepare_filename(info['entries'][0])
        return filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")

# Spotify linkindən mahnı adını çıxart
def get_spotify_track_title(spotify_url):
    try:
        track_id = re.findall(r"track/([a-zA-Z0-9]+)", spotify_url)[0]
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer BQ...SPOTIFY_TOKEN_BURAYA_YAZ"  # Spotify access token burada olmalıdır
        }
        response = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)
        data = response.json()
        title = data['name']
        artist = data['artists'][0]['name']
        return f"{artist} - {title}"
    except:
        return None

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🎧 Spotify və ya mahnı adını göndərin, MP3 şəklində göndərəcəm!")

@app.on_message(filters.text & ~filters.command("start"))
async def mp3_handler(client, message):
    query = message.text.strip()
    await message.reply("🔍 Axtarılır...")

    if "spotify.com/track/" in query:
        track_name = get_spotify_track_title(query)
        if not track_name:
            await message.reply("❌ Spotify linki tanınmadı.")
            return
        query = track_name

    try:
        filename = download_mp3(query)
        await message.reply_audio(audio=filename, caption=f"🎵 {query}")
        os.remove(filename)
    except Exception as e:
        await message.reply(f"❌ Xəta baş verdi:\n`{e}`")

app.run()
