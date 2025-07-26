from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import urllib.parse

TOKEN = "7919152602:AAGG-OYTj_YUm6f42nvtT5uoCg-FcL9IkQI"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salam! Mənə mahnı adı və ya mahnı sözləri göndər, mən sənə alternativ axtarış variantları təqdim edim."
    )

async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not query:
        await update.message.reply_text("Zəhmət olmasa, mahnı adı və ya sözlərini yaz.")
        return

    base_url = "https://www.google.com/search?q="
    variants = [
        query,
        query + " lyrics",
        query + " song"
    ]

    keyboard = [
        [InlineKeyboardButton(text=f"Axtarış variantı {i+1}", url=base_url + urllib.parse.quote(variant))]
        for i, variant in enumerate(variants)
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"\"{query}\" üçün tapılan alternativ axtarışlar:",
        reply_markup=reply_markup
    )

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_song))

    print("Bot işləyir...")
    application.run_polling()

if __name__ == "__main__":
    main()
