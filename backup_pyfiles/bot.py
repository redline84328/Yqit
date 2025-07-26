import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! Mənə şəkil göndər, mən cavab verim.")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Şəkil alındı! Video yaratmaq üçün AI backend-lə inteqrasiya lazımdır.")

async def main():
    BOT_TOKEN = "8116239967:AAEUXR7rWMAqQxKhdms2wVPF85jNq9H-EY8"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("Bot işləyir...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
