import requests
from bs4 import BeautifulSoup
import json


def extract_text(item):
    return item.text if item else None


def get_ad_information(soup):
    ad_info_keys = ['Views', 'Update Date', 'Ad Type', 'Owner Username']
    ad_info_values = [
        extract_text(soup.find('div', class_=f'adPage__aside__stats__{key.lower().replace(" ", "")}'))
        for key in ad_info_keys[:-1]
    ]
    ad_info_values.append(
        extract_text(soup.find('a', class_='adPage__aside__stats__owner__login'))
    )
    return dict(zip(ad_info_keys, [val for val in ad_info_values if val]))


def get_general_information(soup):
    return get_information(
        soup,
        'div',
        'adPage__content__features__col',
        'adPage__content__features__key',
        'adPage__content__features__value'
    )


def get_features(soup):
    return get_information(
        soup,
        'div',
        'adPage__content__features__col grid_7 suffix_1',
        'adPage__content__features__key',
        'adPage__content__features__value'
    )

def get_information(soup, container_type, container_class, key_class, value_class):
    container = soup.find(container_type, class_=container_class)
    information = {}
    if container:
        for item in container.find_all('li'):
            key = extract_text(item.find('span', class_=key_class))
            value = extract_text(item.find('span', class_=value_class))
            if key and value:
                information[key.strip()] = value.strip()
    return information


def extract_info(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    dict_result = {
        'Title': extract_text(soup.find('h1', itemprop='name')),
        'Description': extract_text(soup.find('div', itemprop='description')),
        'Price': None,
        'Location': None,
        'Ad Info': get_ad_information(soup),
        'General Info': get_general_information(soup),
        'Features': get_features(soup)
    }

    # Handling the price and currency
    price = extract_text(soup.find('span', class_='adPage__content__price-feature__prices__price__value'))
    currency = soup.find('span', itemprop='priceCurrency')
    if price:
        if 'negociabil' in price:
            dict_result['Price'] = price
        elif currency:
            dict_result['Price'] = f"{price} {currency.get('content')}"

    # Handling the location
    country = soup.find('meta', itemprop='addressCountry')
    locality = soup.find('meta', itemprop='addressLocality')
    if country and locality:
        dict_result['Location'] = f"{locality.get('content')}, {country.get('content')}"

    print(json.dumps({k: v for k, v in dict_result.items() if v}, indent=4, ensure_ascii=False))
    return {k: v for k, v in dict_result.items() if v}


URL = "https://999.md/ro/81026570"
extract_info(URL)
