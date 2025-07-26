from pyrogram import Client, filters

API_ID = 26345223
API_HASH = "2d82aca171ac54b09a103cccb4ba5c7f"
BOT_TOKEN = "8378651941:AAFNq1_NzTJdXH5ZCNnU4_Xyndgk94lr3Fs"

app = Client("location_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("yer"))
async def yer_handler(client, message):
    try:
        komut = message.text.split(" ", 1)
        if len(komut) < 2:
            await message.reply("❗ İstifadə: /yer <koordinat> <ad>\n\n📍 Nümunə: /yer 40.4093,49.8671 Bakı Bulvarı")
            return

        koordinat_ve_ad = komut[1]
        bolunmus = koordinat_ve_ad.split(" ", 1)
        
        if len(bolunmus) < 2:
            await message.reply("❗ Koordinat və məkan adını tam göndərin.\n\n📍 Nümunə: /yer 40.4093,49.8671 Bakı Bulvarı")
            return

        koordinat, ad = bolunmus
        lat_long = koordinat.strip()
        mekani = ad.strip()

        link = f"https://www.google.com/maps/search/?api=1&query={lat_long}"
        cavab = f"📍 <b>{mekani}</b>\n🌍 <a href='{link}'>Google Maps</a>"

        await message.reply(cavab, parse_mode="html", disable_web_page_preview=True)
    except Exception as e:
        await message.reply(f"❌ Xəta baş verdi:\n<code>{e}</code>", parse_mode="html")

app.run()
