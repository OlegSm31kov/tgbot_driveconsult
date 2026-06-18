import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, filters, \
    Application, ApplicationBuilder

from services.entity_extractor import extract_entities
from services.recommender import recommend_products
from services.intent_classifier import IntentClassifier
from services.response_generator import recommend_response

classifier = IntentClassifier()

async def start(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()
    await update.message.reply_text('Я — бот, который поможет вам выбрать жёсткий диск под ваши задачи и бюджет\n'
                                    'Напишите, какой вам нужен диск - тип, объём, стоимость, для каких задач - и '
                                    'я обязательно что-нибудь подберу')

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Просто напишите, какой вам нужен диск, и я обязательно подберу что-нибудь для вас')

async def give_recommendations(update, context):
    products = recommend_products(context.user_data)

    await update.message.reply_text(
        recommend_response(products)
    )

    context.user_data.clear()

async def run_bot(update: Update, context: CallbackContext) -> None:

    replica = update.message.text
    print(f'replica: {replica}')

    step = context.user_data.get('step')

    match step:
        case 'awaiting_use_case':
            entities = extract_entities(replica)
            context.user_data.update(entities)

            if "use_case" in context.user_data:
                context.user_data["use_case"] = entities["use_case"]
                if context.user_data.get("budget") is None:
                    context.user_data["step"] = "awaiting_budget"
                    await update.message.reply_text('Каков ваш бюджет (в рублях)?')
                else:
                    await give_recommendations(update, context)
            else:
                await update.message.reply_text('Не понял назначение диска(')

            return

        case 'awaiting_budget':
            entities = extract_entities(replica)
            context.user_data.update(entities)

            if "budget" in context.user_data:
                context.user_data["budget"] = entities["budget"]

                await give_recommendations(update, context)

            else:
                await update.message.reply_text("Укажите бюджет числом.")

            return

    intent = classifier.predict(replica)
    print(f'intent: {intent}')

    match intent:
        case 'greet':
            context.user_data['step'] = 'awaiting_use_case'
            await update.message.reply_text('Здравствуйте! Готов помочь вам с выбором диска\n'
                      'Для каких задач вам нужен диск (игры, видео, архив, система)?')

        case 'recommend':
            entities = extract_entities(replica)
            context.user_data.update(entities)

            print(f'entities: {entities}')
            if len(context.user_data) > 0:
                if "use_case" not in context.user_data:
                    context.user_data["step"] = "awaiting_use_case"
                    await update.message.reply_text('Для каких задач вам нужен диск (игры, видео, архив, система)?')
                    return

                elif 'budget' not in context.user_data:
                    context.user_data["step"] = "awaiting_budget"
                    await update.message.reply_text('Каков ваш бюджет?')
                    return

                else:
                    await give_recommendations(update, context)
            else:
                await update.message.reply_text('Для каких задач вам нужен диск (игры, видео, архив, система)?')
                context.user_data['step'] = 'awaiting_use_case'
        case 'buy':
            await update.message.reply_text('Купить можно по ссылке <тут типа ссылка>')


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