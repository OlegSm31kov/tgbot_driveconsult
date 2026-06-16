def recommend_response(products):
    if not products:
        return ('К сожалению, ничего не могу вам предложить(\n'
                'Попробуйте другие параметры, и я обязательно что-нибудь подберу')

    response = 'Могу предложить следующие варианты:'

    for product in products:
        response += (f'\n{product['name']}:'
                     f'\n - тип: {product['type']}:'
                     f'\n - объем: {product['size_gb']} ГБ'
                     f'\n - цена: {product['price']} руб.\n')

    return response