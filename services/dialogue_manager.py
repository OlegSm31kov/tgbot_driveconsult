import random
from sys import intern

from data.responses import GREET_RESPONSES, FAILURE_RESPONSES, BYE_RESPONSES, SMALLTALK_RESPONSES, HOBBY_QUESTIONS

from data.user_profiles import HOBBIES, USE_CASE_MAPPING
from services.entity_extractor import extract_entities
from services.recommender import recommend_products

class DialogManager:

    def __init__(self, classifier, retriever):
        self.classifier = classifier
        self.retriever = retriever

    async def handle_message(self, replica, update, context):
        print(f"replica: {replica}")

        # сначала пытаемся обработать текущий шаг в рекомендации и покупке диска
        step = context.user_data.get("step")
        print(f"step: {step}")
        if step:
            handled = await self._process_step(replica, update, context)
            if handled:
                return

        # если к покупке ещё не перешли, то обрабатываем общее состояние диалога
        dialog_state = context.user_data.get("dialog_state")
        print(f"dialog_state: {dialog_state}")
        if dialog_state:
            handled = await self._process_dialog_state(replica, update, context)
            if handled:
                return

        # если шага нет - определяем intent
        intent, confidence = self.classifier.predict(replica)
        print(f"intent: {intent}\nconfidence: {confidence}")
        if confidence > 0.3:
            await self._process_intent(intent, replica, update, context)
        else:
            answer = self.retriever.get_response(replica)
            if answer:
                await update.message.reply_text(answer)
            else:
                await update.message.reply_text(random.choice(FAILURE_RESPONSES))

    async def _process_dialog_state(self, replica, update, context):
        state = context.user_data.get("dialog_state")
        print(f"dialog_state: {state}")
        match state:
            case "greeting":
                context.user_data["dialog_state"] = "asking_hobby"
                answer = self.retriever.get_response(replica)
                if answer:
                    await update.message.reply_text(answer)
                else:
                    await update.message.reply_text(random.choice(FAILURE_RESPONSES))

                await update.message.reply_text(random.choice(HOBBY_QUESTIONS))
                return True

            case "asking_hobby":
                hobby = self._detect_hobby(replica)
                if hobby:
                    context.user_data["hobby"] = hobby
                if hobby and hobby != "no_hobby":
                    context.user_data["use_case"] = USE_CASE_MAPPING[hobby]
                else:
                    hobby = "no_hobby"
                    context.user_data["hobby"] = "no_hobby"
                    context.user_data["use_case"] = "archive"
                context.user_data["dialog_state"] = "awaiting_ad_response"

                await update.message.reply_text(self._build_advertising_message(hobby))
                return True

            case "awaiting_ad_response":
                intent = (self.classifier.predict(replica))[0]
                print(f"intent: {intent}")

                if intent == "yes":
                    if self._can_recommend(context.user_data):
                        await self._give_recommendations(update, context)
                        return True

                    context.user_data["dialog_state"] = None

                    if "use_case" not in context.user_data:
                        await update.message.reply_text("Отлично, для каких задач нужен диск?")
                        context.user_data["step"] = "awaiting_use_case"
                        return True

                    if "budget" not in context.user_data:
                        context.user_data["step"] = "awaiting_budget"
                        await update.message.reply_text("Каков ваш бюджет?")
                        return True

                if intent == "no":
                    context.user_data["dialog_state"] = None
                    await update.message.reply_text(
                        "Хорошо\nЕсли у вас закончится место и понадобится помощь "
                        "с выбором накопителя — я всегда к вашим услугам"
                    )
                    return True

                await update.message.reply_text(
                    "Не совсем понял\nХотите подобрать накопитель?"
                )
                return True

            case "advertising":
                entities = extract_entities(replica)
                context.user_data.update(entities)

                if self._can_recommend(context.user_data):
                    await self._give_recommendations(update, context)
                    return True

                context.user_data["step"] = "awaiting_budget"

                await update.message.reply_text(
                    "Кстати, если понадобится диск, "
                    "какой у вас бюджет?"
                )

                return True
        return True

    async def _process_step(self, replica, update, context):
        step = context.user_data.get("step")
        match step:
            case "awaiting_use_case":
                self._update_user_data(replica, context)
                if "use_case" not in context.user_data:
                    await update.message.reply_text("Не понял назначение диска\n"
                                                    "Укажите: игры, видео, архив или система")
                    return True

                if "budget" not in context.user_data:
                    context.user_data["step"] = "awaiting_budget"
                    await update.message.reply_text("Каков ваш бюджет?")
                    return True

                await self._give_recommendations(update, context)
                return True

            case "awaiting_budget":
                self._update_user_data(replica, context)
                if "budget" not in context.user_data:
                    await update.message.reply_text("Укажите бюджет числом")
                    return True

                await self._give_recommendations(update, context)
                return True
        return False

    async def _process_intent(self, intent, replica, update, context):
        print(f"intent: {intent}")
        match intent:
            case "greet":
                context.user_data["dialog_state"] = "greeting"
                await update.message.reply_text(random.choice(GREET_RESPONSES))
                return

            case "recommend":
                entities = extract_entities(replica)
                context.user_data.update(entities)
                if self._can_recommend(context.user_data):
                    await self._give_recommendations(update, context)
                    return

                if "budget" not in context.user_data:
                    context.user_data["step"] = "awaiting_budget"
                    await update.message.reply_text("Каков ваш бюджет?")
                    return

                if "use_case" not in context.user_data:
                    context.user_data["step"] = "awaiting_use_case"
                    await update.message.reply_text("Для каких задач нужен диск?")
                    return

            case "buy":
                await update.message.reply_text("Купить можно по ссылке: "
                                                "<ссылка>")

            case "smalltalk":
                answer = self.retriever.get_response(replica)
                if answer:
                    await update.message.reply_text(answer)
                else:
                    await update.message.reply_text(random.choice(FAILURE_RESPONSES))

            case "bye":
                context.user_data.clear()
                await update.message.reply_text(random.choice(BYE_RESPONSES))

            case _:
                await update.message.reply_text(random.choice(FAILURE_RESPONSES))

    def _detect_hobby(self, text):
        text = text.lower()

        for hobby_name, hobby_data in HOBBIES.items():
            for keyword in hobby_data["keywords"]:
                if keyword in text:
                    return hobby_name

        return None

    def _build_advertising_message(self, hobby):
        return HOBBIES[hobby]["ad_message"] + "\nМогу помочь подобрать накопитель"

    async def _give_recommendations(self, update, context):
        products = recommend_products(context.user_data)
        if not products:
            answer =('К сожалению, ничего не могу вам предложить(\n '
                     'Попробуйте другие параметры, и я обязательно что-нибудь подберу')

        else:
            answer = 'Могу предложить следующие варианты:\n'

            for product in products:
                answer += (f'\n{product['name']}:'
                             f'\n - тип: {product['type']}'
                             f'\n - объем: {product['size_gb']} ГБ'
                             f'\n - цена: {product['price']} руб.\n')

        await update.message.reply_text(answer)
        context.user_data.clear()

    def _update_user_data(self, replica, context):
        entities = extract_entities(replica)
        context.user_data.update(entities)

    def _can_recommend(self, user_data):

        useful_entities = [
            "type",
            "budget",
            "use_case",
            "size_gb"
        ]

        count = sum(key in user_data for key in useful_entities)
        return count >= 2