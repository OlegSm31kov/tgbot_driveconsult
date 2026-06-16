import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, filters, \
    Application, ApplicationBuilder

from services.entity_extractor import extract_entities
from services.recommender import recommend_products
from services.intent_classifier import IntentClassifier
from services.response_generator import recommend_response


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет, проверка связи :)')

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Однажды здесь будет помощь...')

async def run_bot(update: Update, context: CallbackContext) -> None:
    replica = update.message.text
    print(f'replica: {replica}')

    classifier = IntentClassifier()
    intent = classifier.predict(replica)
    print(f'intent: {intent}')

    answer = 'Пу-пу-пу, чё-то я не знаю, что ответить'
    match intent:
        case 'greet':
            answer = 'И вам не хворать'
        case 'recommend':
            entities = extract_entities(replica)
            print(f'entities: {entities}')
            if len(entities) > 0:
                products = recommend_products(entities)
                answer = recommend_response(products)
            else: answer = 'Укажите, какие параметры вам важны'
        case 'buy':
            answer = 'Купить можно по ссылке <тут типа ссылка>'

    await update.message.reply_text(answer)

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

    intent_classifier = IntentClassifier()

if __name__ == "__main__":
    main()