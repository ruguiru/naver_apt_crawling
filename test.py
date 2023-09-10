import re

def extract_price(text: str):
    text = text.replace(' ', '')
    dealtype = text[:2]
    text = text[2:]
    price = 0
    wolse = 0
    price_str = ''
    if dealtype == '월세':
        wolse_str = text.replace(',', '')
        if wolse_str.find('/') != -1:
            parts = wolse_str.split('/')
            price_str = parts[0]
            wolse = int(parts[1])
        else:
            wolse = int(wolse_str)
            return dealtype, 0, wolse
    else:
        price_str = text.split('(')[0].replace(',', '')

    if price_str.find('억') != -1:
        parts = price_str.split('억')
        if parts[1]:
            price = int(parts[0]) * 10000 + int(parts[1])
        else:
            price = int(parts[0]) * 10000
    else:
        price = int(price_str)

    return dealtype, price, wolse

# print(extract_price('매매 6억(1,370만원/3.3㎡)'))
# print(extract_price('매매 5억 8,500(1,370만원/3.3㎡)'))
# print(extract_price('전세 9,500(1,370만원/3.3㎡)'))
# print(extract_price('전세 2억 500(1,370만원/3.3㎡)'))
# print(extract_price('월세 1억/100'))
# print(extract_price('월세 1억 500/100'))
# print(extract_price('월세 50'))


caching = set()

caching.add((1, 'abc'))
caching.add((2, 'abc'))
caching.add((1, 'ab'))

if (1, 'ab') in caching:
    print('find')

print(caching)

