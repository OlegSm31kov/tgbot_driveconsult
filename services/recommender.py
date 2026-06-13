import json
from pathlib import Path

def load_products():
    json_path = Path(__file__).parent.parent / 'data' / 'products.json'
    with json_path.open('r', encoding='utf-8') as json_data:
        products = json.load(json_data)
    return products

def recommend_products(use_case, budget):
    products = load_products()
    options = []
    for product in products:
        if use_case in product['use_case'] and product['price'] <= budget:
            options.append(product['name'])
    return options