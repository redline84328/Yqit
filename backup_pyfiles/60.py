from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

API_TOKEN = "8492715732:AAGL_BYIzQUcbzlJ78kcUBHJM8USl5uVkIQ"
TZDB_API_KEY = "C982NIALOH5M"

# 🔹 Start komandası
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌍 Hər hansı bir şəhərin adını yaz: məsələn London, Bakı, Tokyo və s.\n\nMən sənə o şəhərin saatını deyəcəyəm.")

# 🔹 Şəhər adı ilə saat alma
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()

    # 1. Şəhərin koordinatlarını al (OpenStreetMap)
    geocode_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
    geo_response = requests.get(geocode_url).json()

    if not geo_response:
        await update.message.reply_text("❌ Şəhər tapılmadı. Zəhmət olmasa, dəqiq ad daxil et.")
        return

    lat = geo_response[0]['lat']
    lon = geo_response[0]['lon']
    display_name = geo_response[0]['display_name']

    # 2. Koordinatla saat al (TimeZoneDB)
    tz_url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={TZDB_API_KEY}&format=json&by=position&lat={lat}&lng={lon}"
    tz_response = requests.get(tz_url).json()

    if tz_response["status"] != "OK":
        await update.message.reply_text("❌ Saat məlumatı tapılmadı.")
        return

    time_str = tz_response["formatted"]
    zone = tz_response["zoneName"]

    # 3. Cavab göndər
    await update.message.reply_text(
        f"📍 <b>{display_name}</b>\n🕒 Saat: <b>{time_str}</b>\n🧭 Zaman zonası: <code>{zone}</code>",
        parse_mode="HTML"
    )

# 🔹 Botu işə sal
if __name__ == "__main__":
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_time))

    print("🟢 Bot işə düşdü...")
    app.run_polling()
