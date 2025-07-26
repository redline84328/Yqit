import os
import uuid
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Telegram Bot Token
TOKEN = "8378651941:AAFNq1_NzTJdXH5ZCNnU4_Xyndgk94lr3Fs"

# Varsayılan dil
kullanici_dili = "tr"

# Çok dilli mesajlar
MESAJ = {
    "tr": {
        "hosgeldin": "Merhaba! YouTube linki gönder, müzik ya da video olarak indireyim.",
        "secim": "Ne indirmek istersin?",
        "kalite_sec": "İndirme kalitesini seç:",
        "indiriliyor": "İndiriliyor, lütfen bekleyin...",
        "tamam": "Dosya gönderiliyor...",
        "hata": "Bir hata oluştu:",
        "gecersiz": "Lütfen geçerli bir YouTube bağlantısı gönder.",
        "dil_degisti": "Dil Türkçe olarak ayarlandı.",
    },
    "az": {
        "hosgeldin": "Salam! YouTube linkini göndər, musiqi və ya video olaraq yükləyim.",
        "secim": "Nə yükləmək istəyirsən?",
        "kalite_sec": "Keyfiyyət seçin:",
        "indiriliyor": "Yüklənir, zəhmət olmasa gözləyin...",
        "tamam": "Fayl göndərilir...",
        "hata": "Xəta baş verdi:",
        "gecersiz": "Zəhmət olmasa keçərli bir YouTube linki göndərin.",
        "dil_degisti": "Dil Azərbaycan dili olaraq dəyişdirildi.",
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESAJ[kullanici_dili]["hosgeldin"])

async def dil_degistir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global kullanici_dili
    if "az" in update.message.text:
        kullanici_dili = "az"
    else:
        kullanici_dili = "tr"
    await update.message.reply_text(MESAJ[kullanici_dili]["dil_degisti"])

async def gelen_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    if "youtube.com" not in link and "youtu.be" not in link:
        await update.message.reply_text(MESAJ[kullanici_dili]["gecersiz"])
        return

    buttons = [
        [InlineKeyboardButton("MP3 (Müzik)", callback_data=f"sec|mp3|{link}")],
        [InlineKeyboardButton("MP4 (Video)", callback_data=f"sec|mp4|{link}")]
    ]
    await update.message.reply_text(
        MESAJ[kullanici_dili]["secim"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def kalite_sec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, tur, link = query.data.split("|")

    if tur == "mp3":
        buttons = [
            [InlineKeyboardButton("128 kbps", callback_data=f"indir|mp3|128|{link}")],
            [InlineKeyboardButton("320 kbps", callback_data=f"indir|mp3|320|{link}")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("360p", callback_data=f"indir|mp4|360|{link}")],
            [InlineKeyboardButton("720p", callback_data=f"indir|mp4|720|{link}")],
            [InlineKeyboardButton("1080p", callback_data=f"indir|mp4|1080|{link}")]
        ]

    await query.edit_message_text(
        MESAJ[kullanici_dili]["kalite_sec"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def indir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, tur, kalite, link = query.data.split("|")

    await query.edit_message_text(MESAJ[kullanici_dili]["indiriliyor"])

    try:
        hedef_dosya = None

        if tur == "mp3":
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': "%(title)s.%(ext)s",
                'ffmpeg_location': '/data/data/com.termux/files/usr/bin/ffmpeg',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': kalite,
                }],
            }
        else:
            dosya_id = str(uuid.uuid4())
            ydl_opts = {
                'format': f'bestvideo[height<={kalite}]+bestaudio/best',
                'outtmpl': f"{dosya_id}.mp4",
                'merge_output_format': 'mp4',
                'ffmpeg_location': '/data/data/com.termux/files/usr/bin/ffmpeg',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if tur == "mp3":
                info = ydl.extract_info(link, download=True)
                hedef_dosya = f"{info['title']}.mp3"
            else:
                ydl.download([link])
                hedef_dosya = f"{dosya_id}.mp4"

        if not os.path.exists(hedef_dosya):
            raise FileNotFoundError(f"{hedef_dosya} bulunamadı!")

        await query.message.reply_text(MESAJ[kullanici_dili]["tamam"])

        if tur == "mp3":
            await query.message.reply_audio(audio=open(hedef_dosya, "rb"))
        else:
            await query.message.reply_video(video=open(hedef_dosya, "rb"))

        os.remove(hedef_dosya)

    except Exception as e:
        await query.message.reply_text(f"{MESAJ[kullanici_dili]['hata']} {str(e)}")

# Botu başlat
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("dil", dil_degistir))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gelen_link))
app.add_handler(CallbackQueryHandler(kalite_sec, pattern="^sec"))
app.add_handler(CallbackQueryHandler(indir, pattern="^indir"))

print("Bot çalışıyor...")
app.run_polling()
