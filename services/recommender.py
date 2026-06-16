import json
from pathlib import Path

def load_products():
    json_path = Path(__file__).parent.parent / 'data' / 'products.json'
    with json_path.open('r', encoding='utf-8') as json_data:
        products = json.load(json_data)
    return products

def recommend_products(entities):
    products = load_products()
    options = []

    use_case = entities.get('use_case')
    d_type = entities.get('type')
    budget = entities.get('budget', float('inf'))
    price_category = entities.get('price_category')

    for product in products:
        if (
                (use_case is None or use_case in product['use_case'])
                and (d_type is None or d_type in product['type'])
                and product['price'] <= budget
        ):
            options.append(product)

    if price_category == 'cheap':
        options = sorted(options, key=lambda x: x['price'])
        return options[:3]

    if price_category == 'premium':
        options = sorted(options, key=lambda x: x['price'], reverse=True)
        return options[:3]

    return options