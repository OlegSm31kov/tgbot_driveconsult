import re

def extract_entities(text: str):
    text = text.lower()

    entities = {}

    # тип диска
    if 'ssd' in text:
        entities['type'] = 'SSD'
    elif 'hdd' in text:
        entities['type'] = 'HDD'

    # назначение
    if 'игр' in text:
        entities['use_case'] = 'games'
    elif 'видео' in text:
        entities['use_case'] = 'video'
    elif 'архив' in text:
        entities['use_case'] = 'archive'

    # бюджет
    if 'недорог' in text or 'дешев' or 'дешёв' in text or 'бюджетн' in text:
        entities['price_category'] = 'cheap'

    if 'дорог' in text or 'премиум' in text:
        entities['price_category'] = 'premium'

    budget_match = re.search(r'(\d+)\s*(руб|р)?', text)
    if budget_match:
        entities['budget'] = int(budget_match.group(1))

    return entities