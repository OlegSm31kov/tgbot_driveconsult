import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, filters, ApplicationBuilder

from services.dialogue_manager import DialogManager
from services.recommender import recommend_products
from services.intent_classifier import IntentClassifier
from services.dialogue_retriever import DialogueRetriever

classifier = IntentClassifier()
retriever = DialogueRetriever('data/dialogues_dataset.txt')
dialog_manager = DialogManager(classifier, retriever)

async def start(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()
    await update.message.reply_text('Я — бот, который не прочь поболтать)\n'
                                    'А если вдруг вам нужен жёсткий диск - '
                                    'я обязательно что-нибудь подберу')

async def give_recommendations(update, context):
    products = recommend_products(context.user_data)

    if not products:
        return ('К сожалению, ничего не могу вам предложить(\n'
                'Попробуйте другие параметры, и я обязательно что-нибудь подберу')

    response = 'Могу предложить следующие варианты:\n'

    for product in products:
        response += (f'\n{product['name']}:'
                     f'\n - тип: {product['type']}'
                     f'\n - объем: {product['size_gb']} ГБ'
                     f'\n - цена: {product['price']} руб.\n')

    await update.message.reply_text(response)

    context.user_data.clear()

async def run_bot(update: Update, context: CallbackContext) -> None:
    replica = update.message.text

    await dialog_manager.handle_message(replica, update, context)

def main():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_bot))

    application.run_polling()

if __name__ == "__main__":
    main()