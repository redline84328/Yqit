from pyrogram import Client, filters
from pyrogram.types import Message

# BOT məlumatlarını bura yaz
app = Client(
    "map_bot",
    api_id=26345223,
    api_hash="2d82aca171ac54b09a103cccb4ba5c7f",
    bot_token="8378651941:AAFNq1_NzTJdXH5ZCNnU4_Xyndgk94lr3Fs"
)

@app.on_message(filters.command("yer"))
async def yer_handler(client, message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("⛔️ İstifadə: /yer 40.4093,49.8671 Bakı Bulvarı")
            return

        # Parametrləri ayırırıq
        data = args[1].split(maxsplit=1)
        koordinat = data[0]
        ad = data[1] if len(data) > 1 else "Məkan"

        # Enlem və boylam
        lat, lon = map(float, koordinat.strip().split(","))

        # Google Maps linki
        maps_link = f"https://maps.google.com/?q={lat},{lon}"

        # Mesaj – parse_mode YOXDUR, sadə textdir
        text = f"📍 {ad}\n📌 {lat}, {lon}\n🌐 Google Maps: {maps_link}"

        await message.reply(text)
    except Exception as e:
        await message.reply(f"❌ Xəta baş verdi:\n{e}")

app.run()
