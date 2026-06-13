import os
from itertools import product

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, filters, \
    Application, ApplicationBuilder

from services.recommender import recommend_products


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет, проверка связи :)')

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Однажды здесь будет помощь...')

async def run_bot(update: Update, context: CallbackContext) -> None:
    replica = update.message.text

    user_use_case = 'None'

    if 'игр' in replica:
        user_use_case = 'games'
    if 'видео' in replica:
        user_use_case = 'video'

    products = recommend_products(user_use_case, 15000)
    if len(products) > 0:
        answer = 'Вам подойдут:\n'
        for product in products:
            answer += f'- {product}\n'
    else: answer = 'Не могу ничего вам предложить('

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