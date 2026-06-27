import json
from pathlib import Path

from data.user_profiles import USE_CASE_PRIORITIES


def load_products():
    json_path = Path(__file__).parent.parent / 'data' / 'products.json'
    with json_path.open('r', encoding='utf-8') as json_data:
        products = json.load(json_data)
    return products

def recommend_products(entities):
    filtered_products = filter_products(entities)

    if entities.get("use_case") is None:
        return filtered_products

    filtered_products.sort(
        key=lambda p: calculate_score(
            p, USE_CASE_PRIORITIES[entities["use_case"]]
        ),
        reverse=True
    )
    return filtered_products


def calculate_score(product, priorities):
    score = 0
    score += product["speed_mb_s"] * priorities["speed_weight"]
    score += product["size_gb"] * priorities["size_weight"]
    score -= product["price"] / 1000 * priorities["price_weight"]
    if product["type"] == priorities["preferred_type"]:
        score += 1000
    return score

def filter_products(entities):
    products = load_products()
    options = []

    d_type = entities.get('type')
    if d_type is None and entities.get('use_case'):
        d_type = USE_CASE_PRIORITIES[entities["use_case"]].get("preferred_type")
    size = entities.get('size_gb')
    budget = entities.get('budget', float('inf'))

    for product in products:
        if (
                (size is None or size <= product['size_gb'])
                and (d_type is None or d_type in product['type'])
                and product['price'] <= budget
        ):
            options.append(product)

    return options