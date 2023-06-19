from random import choice
import json
from bs4 import BeautifulSoup
import requests
import csv

desktop_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko)'
    ' Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']


def random_agent():
    return {'User-Agent': choice(desktop_agents), 'Accept': 'text/html,application/xhtml+xml,application/xml; q=0.9'}


def search_info(url, item_text):
    pages_count = 1
    page = 1
    data_info = []
    while True:
        reg = requests.get(url + f'?count=80&Item_page={page}', headers=random_agent())
        soup = BeautifulSoup(reg.text, 'lxml')
        rows = soup.find_all('tr')[1:]
        for row in rows:
            colum_s = row.find_all('td')
            if len(colum_s):
                name_item = colum_s[1].text.strip().replace('/', '_')
                art_item = colum_s[2].text.strip()
                color_item = colum_s[3].text.strip()
                item_availability = colum_s[4].text.strip()
                item_cost = colum_s[5].getText(strip=True).replace(u'\xa0', u'')
                item_remainder = colum_s[-1].find('a')['data-remainder']
                if not len(item_remainder):
                    item_remainder = 0
                else:
                    item_remainder = float(item_remainder)

                data_dict = {'Название': name_item, 'Артикул': art_item, 'Цвет': color_item,
                             'Наличие': item_availability, 'Цена': item_cost,
                             'Остаток': item_remainder, 'Группа': item_text}
                data_info.append(data_dict)
                data_csv.append(data_dict)
        print(f'Now we working with page {page}, and recording data')
        page += 1

        for elem in soup.find_all(class_='last'):
            if 'Последняя' in elem.text:
                str_form = str(elem)
                first_ind = str_form.find('Item_page')
                pages_count = int(str_form[first_ind + 10:str_form.find('>', first_ind) - 1])
        if page > pages_count:
            return data_info


url = 'https://www.dara-hobby.ru/'
req = requests.get(url, headers=random_agent())
all_groups_dict = {}
data_csv = []
field_names = ['Название', 'Артикул', 'Цвет', 'Наличие', 'Цена', 'Остаток', 'Группа']
soup = BeautifulSoup(req.text, 'lxml')
for item in (soup.find_all('div', class_='fon_li')):
    href_list = item.find_all('a')
    if len(href_list):
        href = url + href_list[0].get('href')
        data_info = search_info(href, item.text)
        all_groups_dict[href] = (item.text, data_info)
        print(f'{item.text} was recorded...')

with open('data/total.csv', 'w', encoding='cp1251', newline='') as file:
    writer = csv.DictWriter(file, delimiter=';', fieldnames=field_names, skipinitialspace=True)
    writer.writeheader()
    writer.writerows(data_csv)

with open('data/all_groups_dict.json', 'w', encoding='utf-8') as file:
    json.dump(all_groups_dict, file, indent=4, ensure_ascii=False)

print('{+} ФАЙЛ total.csv УСПЕШНО ЗАПИСАН')

