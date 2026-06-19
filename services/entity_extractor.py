import re

def extract_entities(text: str):
    text = text.lower()

    entities = {}

    # тип диска
    if 'ssd' in text:
        entities['type'] = 'SSD'
    elif 'hdd' in text:
        entities['type'] = 'HDD'

    #
    size_match = re.search(r"(\d+)\s*(тб|tb)", text)
    if size_match:
        entities['size_gb'] = int(size_match.group(1)) * 1024

    size_match = re.search(r"(\d+)\s*(гб|gb)", text)
    if size_match:
        entities['size_gb'] = int(size_match.group(1))

    # назначение
    if 'игр' in text:
        entities['use_case'] = 'games'
    elif 'видео' in text:
        entities['use_case'] = 'video'
    elif 'архив' in text:
        entities['use_case'] = 'archive'
    elif 'систем' in text:
        entities['use_case'] = 'system'

    # бюджет
    if 'недорог' in text or 'дешев'  or 'дешёв' in text or 'бюджетн' in text:
        entities['price_category'] = 'cheap'

    if 'дорог' in text or 'премиум' in text:
        entities['price_category'] = 'premium'

    budget_match = re.search(r"(\d+)\s*(к|тыс|тысяч|тыщи)\b", text)
    if budget_match:
        entities['budget'] = int(budget_match.group(1)) * 1000

    if 'budget' not in entities:
        budget_match = re.search(r'(\d+)\s*(руб|р)?', text)
        if budget_match:
            entities['budget'] = int(budget_match.group(1))

    return entities