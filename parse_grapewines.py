import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import csv


agent = UserAgent()


with open('data.csv', 'w') as F:
    writer = csv.writer(F)
    writer.writerow([
        'image url', 'Article', 'Name_eng', 'Name_rus', 'st_price', 'promo_price',
        'type', 'sugar', 'color', 'country', 'region', 'subregion', 'appelasion', 'sort', 'extract', 'type_b',
        'alc', 'size', 'temperature', 'organoleptica', 'comp', 'about'
    ])

with open('data.txt', 'w') as F:
    writer = csv.writer(F)
    writer.writerow([
        'name_eng', 'name_rus'
    ])

def parse_cat(agent=agent):
    url = 'https://grapewines.ru/catalog/'
    pagination = requests.get(url=url, params={
        'user-agent': f'{agent.random}'
    }).text
    pages_count = int(BeautifulSoup(pagination, 'lxml').find_all('a', class_='pagination-number')[-1].text)
    card_links = list()
    for page in range(1, pages_count+1):
        new_url = f'https://grapewines.ru/catalog/?PAGEN_3={page}'
        response = requests.get(url=new_url, params={
            'user-agent': f'{agent.random}'
        }).text
        soup = BeautifulSoup(response, 'lxml').find_all('a', class_='card-list__name')
        for link in soup:
            card_links.append('https://grapewines.ru' + link.get('href'))
    count = 0
    for card in card_links:
        response = requests.get(url=card, params={
            'user-agent': f'{agent.random}'
        }).content
        soup = BeautifulSoup(response, 'lxml')
        image_url = 'https:' + soup.find('div', class_='detail-info').find_previous('img').get('src')
        article = soup.find_all('div', class_='detail-info__code')[0].text.strip().split(': ')[1]
        eng_name = soup.find('div', class_='detail-title').find_next('h1').text.replace('\n', '')
        eng_name = re.sub(r'\s+', ' ', eng_name).strip()
        rus_name = soup.find('div', class_='detail-subtitle').text.replace('\n', '')
        rus_name = re.sub(r'\s+', ' ', rus_name).strip()
        price = soup.find('div', class_='detail-price__current').text.replace('₽', 'Р').strip()

        # print(image_url, article, eng_name, rus_name, price, type_prod, country, region, size, sep='\n')
        info_char = soup.find_all('div', class_='detail-info__prop')
        main_char_dict = {}
        for i in info_char:
            title = i.find_next('div', class_='detail-info__prop--title').text.replace(':', '')
            value = i.find_next('div', class_='detail-info__prop--value').text
            value = re.sub(r'\s+', ' ', value).strip().replace(' , ', ',').split(',')
            if len(value) > 1:
                main_char_dict[title] = value
            else:
                main_char_dict[title] = value[0]
        about_style = soup.find_all('div', class_='detail-about__prop')
        style_wine = dict()
        for i in about_style:
            title = i.find_next('div', class_='detail-about__prop--title').text.replace(':', '')
            value = i.find_next('div', class_='detail-about__prop--description').text.replace('"', '').replace(': ', '')
            value = re.sub(r'\s+', ' ', value).strip().capitalize()
            style_wine[title] = value

        type_product = ''
        sugar = ''
        color = ''
        if type(main_char_dict['Тип продукта']) == list:
            type_product = main_char_dict['Тип продукта'][0]
            sugar = main_char_dict['Тип продукта'][2]
            color = ''
        else:
            type_product = main_char_dict['Тип продукта']
            sugar = 'None'
        if len(color) == 0:
            if 'Цвет' in list(style_wine.keys()):
                color = style_wine['Цвет']
            else:
                color = 'None'
        country = ''
        region = ''
        appel = ''
        subregion = ''
        if type(main_char_dict['Страна']) == list:
            country = main_char_dict['Страна'][0]
            region = main_char_dict['Страна'][1]
            if len(main_char_dict['Страна']) == 2:
                appel = 'None'
            if len(main_char_dict['Страна']) == 3 and len(main_char_dict['Страна'][2]) < 5:
                appel = main_char_dict['Страна'][2]
                subregion = 'None'
            if len(main_char_dict['Страна']) == 3 and len(main_char_dict['Страна'][2]) > 5:
                appel = 'None'
                subregion = main_char_dict['Страна'][2]
            if len(main_char_dict['Страна']) == 4:
                appel = main_char_dict['Страна'][3]
                subregion = main_char_dict['Страна'][2]
        else:
            country = main_char_dict['Страна']

        sort_sos = ''
        if 'Сортовой состав' in list(main_char_dict.keys()):
            if type(main_char_dict['Сортовой состав']) == list:
                sort_sos = ' '.join(main_char_dict['Сортовой состав'])
            if type(main_char_dict['Сортовой состав']) == str:
                sort_sos = main_char_dict['Сортовой состав']
        else:
            sort_sos = 'None'

        extract = ''
        if 'Выдержка' in list(style_wine.keys()):
            extract = style_wine['Выдержка']
        else:
            extract = 'None'
        #Нет типа бочек
        alc = ''
        if 'Крепость' in list(main_char_dict.keys()):
            alc = main_char_dict['Крепость']
        else:
            alc = 'None'
        try:
            size = soup.find_all('div', class_='detail-offers__list')[1].find_all('a', class_='detail-offers__item--label')[1].text
            size = re.sub(r'\s+', ' ', size).strip()
        except IndexError:
            size = 'None'

        temp = ''
        if 'Температура подачи' in list(style_wine.keys()):
            temp = style_wine['Температура подачи']
        else:
            temp = 'None'

        smell = ''
        if 'Аромат' in list(style_wine.keys()):
            smell = style_wine['Аромат']
        else:
            smell = 'None'

        taste = ''
        if 'Вкус' in list(style_wine.keys()):
            taste = style_wine['Вкус']
        else:
            taste = 'None'
        comp = ''
        for i in list(style_wine.keys()):
            if 'сочетаемость' in i.lower():
                comp = style_wine[i]
                break
            else:
                comp = 'None'

        more_about = soup.find_all('a', class_='detail-about__more')
        about = ''
        if len(more_about) != 0:
            about = more_about[0]
            print(about)
        org = smell + '.' + taste
        with open('data.txt', 'a', encoding='utf-8') as F:
            writer = csv.writer(F, delimiter='|')
            writer.writerow([
                eng_name, rus_name
            ])
        with open('data.csv', 'a', encoding='utf-8') as F:
            writer = csv.writer(F)
            writer.writerow([
                image_url, article, eng_name, rus_name,
                price, 'None', type_product, sugar, color,
                country, region, subregion, appel, sort_sos, extract,
                'None', alc, size, temp, org, comp, about
            ])
        count += 1
        print(count)


def main():
    parse_cat()


if __name__ == '__main__':
    main()