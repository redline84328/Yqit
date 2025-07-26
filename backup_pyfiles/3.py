from pyrogram import Client, filters
from pyrogram.types import Message

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
            await message.reply("ℹ️ İstifadə: /yer 40.4093,49.8671 Bakı Bulvarı")
            return

        data = args[1].split(maxsplit=1)

        if ',' not in data[0]:
            await message.reply("⚠️ Koordinatlar düzgün formatda deyil. Belə yaz:\n`40.4093,49.8671`")
            return

        koordinat = data[0]
        ad = data[1] if len(data) > 1 else "Məkan"

        lat_str, lon_str = koordinat.split(',')
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())

        maps_link = f"https://maps.google.com/?q={lat},{lon}"

        text = f"📍 {ad}\n📌 {lat}, {lon}\n🌐 {maps_link}"

        await message.reply(text)
    except Exception as e:
        await message.reply(f"❌ Xəta baş verdi:\n{str(e)}")

app.run()
