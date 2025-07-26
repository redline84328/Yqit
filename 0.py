from pyrogram import Client, filters
from PIL import Image
import pytesseract
import os

API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "7919152602:AAGG-OYTj_YUm6f42nvtT5uoCg-FcL9IkQI"

app = Client(
    "ocr_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.photo)
async def photo_to_text(client, message):
    # Şəkli endir
    file_path = await message.download()
    try:
        # Şəkili aç və OCR et
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='eng+aze')
    except Exception as e:
        await message.reply(f"Xəta baş verdi: {e}")
        return
    finally:
        # Faylı sil
        if os.path.exists(file_path):
            os.remove(file_path)

    if text.strip():
        # Monospace (kod bloku) ilə cavab ver
        await message.reply(f"```\n{text}\n```", parse_mode="markdown")
    else:
        await message.reply("Şəkildə mətn tapılmadı.")

app.run()
