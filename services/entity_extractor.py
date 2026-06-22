import re

from services.text_preprocessor import preprocess


def extract_entities(text: str):
    text = preprocess(text)

    entities = {}

    # тип диска
    ssd_keywords = ['ssd', 's s d', 'ссд', 'эсэсдэ', 'эс эс дэ', 'эсэсди', 'эс эс ди', 'твердотел']
    hdd_keywords = ['hdd', 'h d d', 'шдд', 'ашдиди', 'аш ди ди', 'ди ди', 'винчестер', 'жд']

    if any(k in text for k in ssd_keywords):
        entities['type'] = 'SSD'
    elif any(k in text for k in hdd_keywords):
        entities['type'] = 'HDD'

    # объём
    size_match = re.search(r"(\d+)\s*(тб|tb|терабайт)", text)
    if size_match:
        entities['size_gb'] = int(size_match.group(1)) * 1000

    size_match = re.search(r"(\d+)\s*(гб|gb|гигабайт)", text)
    if size_match:
        entities['size_gb'] = int(size_match.group(1))

    # назначение
    if 'игра' in text:
        entities['use_case'] = 'games'
    elif 'видео' in text:
        entities['use_case'] = 'video'
    elif 'архив' in text:
        entities['use_case'] = 'archive'
    elif 'система' in text:
        entities['use_case'] = 'system'

    # бюджет
    if 'недорог' in text or 'дешев' in text or 'бюджетн' in text:
        entities['price_category'] = 'cheap'

    if 'дорог' in text or 'премиум' in text:
        entities['price_category'] = 'premium'

    budget_match = re.search(r"(\d+)\s*(к|тыс|тысяча|тысяч)\b", text)
    if budget_match:
        entities["budget"] = int(budget_match.group(1)) * 1000

    budget_match = re.search(r"(\d+)\s*(руб|рублей|р)\b",text)
    if budget_match:
        entities["budget"] = int(budget_match.group(1))

    return entities