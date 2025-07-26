from pyrogram import Client, filters
from PIL import Image
import pytesseract
import io
import os

API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "8077981900:AAFVsfEUPm-IwTzN7RV5TwhGVJs0TMu0ffk"

app = Client("ocr_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.photo)
async def photo_to_text(client, message):
    # Şəkli endir
    file = await message.download()
    
    # Şəkli aç
    image = Image.open(file)
    
    # OCR ilə mətn oxu
    text = pytesseract.image_to_string(image, lang='eng+aze')  # Azərbaycan dili üçün 'aze' və ingilis dili
    
    # Faylı sil
    os.remove(file)
    
    if text.strip():
        await message.reply(f"📋 Şəkildəki mətn:\n\n{text}")
    else:
        await message.reply("⚠️ Şəkildə mətn tapılmadı.")

app.run()
