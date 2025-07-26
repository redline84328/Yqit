

from telegram import Update, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def yer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Zəhmət olmasa belə yaz: /yer 40.4093,49.8671 Bakı Bulvarı")
            return

        koordinat = args[0]
        ad = ' '.join(args[1:])
        lat, lon = koordinat.split(',')

        maps_link = f"https://maps.google.com/?q={lat},{lon}"
        text = f"<b>{ad}</b>\n📍 <a href=\"{maps_link}\">{lat}, {lon}</a>"

        await update.message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"Xəta baş verdi: {e}")

app = ApplicationBuilder().token("8378651941:AAFNq1_NzTJdXH5ZCNnU4_Xyndgk94lr3Fs").build()
app.add_handler(CommandHandler("yer", yer))
app.run_polling()
