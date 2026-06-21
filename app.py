import os
import random

from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, filters, ApplicationBuilder, \
    CallbackQueryHandler

from services.dialogue_manager import DialogManager, showcase_callback
from services.recommender import recommend_products
from services.intent_classifier import IntentClassifier
from services.dialogue_retriever import DialogueRetriever
from services.stt_recogniser import recognize_voice

classifier = IntentClassifier()
retriever = DialogueRetriever('data/dialogues_dataset.txt')
dialog_manager = DialogManager(classifier, retriever)

async def start(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()
    await update.message.reply_text('Я — бот, который не прочь поболтать)\n'
                                    'А если вдруг вам нужен жёсткий диск - '
                                    'я обязательно что-нибудь подберу')

async def run_bot(update: Update, context: CallbackContext, replica_override=None) -> None:
    replica = (replica_override if replica_override else update.message.text)

    await dialog_manager.handle_message(replica, update, context)

async def handle_voice(update: Update, context: CallbackContext) -> None:
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    with NamedTemporaryFile(suffix=".ogg", delete=False) as temp_ogg:
        ogg_path = temp_ogg.name

    try:
        await file.download_to_drive(ogg_path)
        replica = recognize_voice(ogg_path)
        print(f"voice recognised: {replica}")

        if not replica:
            await update.message.reply_text(random.choice(["Боюсь, я не понимаю вас(",
                                                          "Не могу понять, что вы говорите("]))
            return

        await run_bot(update, context, replica_override=replica)

    finally:
        if os.path.exists(ogg_path):
            os.remove(ogg_path)

async def error_handler(update, context):
    print(context.error)

def main():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_bot))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(CallbackQueryHandler(showcase_callback))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == "__main__":
    main()