import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, filters, \
    Application, ApplicationBuilder

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет, проверка связи :)')

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Однажды здесь будет помощь...')

async def run_bot(update: Update, context: CallbackContext) -> None:
    replica = update.message.text
    answer = f"Писклявым голосом: \"{replica}\""

    await update.message.reply_text(answer)

    # print(stats)
    print(replica)
    print(answer)
    print()

def main():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_bot))

    application.run_polling()

if __name__ == "__main__":
    main()