import random
import re
import requests
from bs4 import BeautifulSoup
import lxml
import json
import csv
from time import sleep

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}
job_word_keys = {'Парс', 'парс', 'скрейп', 'Скрейп', 'сайт', 'Сайт'}

# забирает стартовую страницу, где будем искать оглавления
def start_parce(url, params=None, test_print=False):
    try:
        r = requests.get(url, headers=headers, params=params)
        print(f'Страница {url}\nзакодирована в {r.encoding}\n')
        if r.status_code == 200:
            src = r.text
            if test_print:
                if '!DOCTYPE' in src:
                    print(f'Страница {url}\nуспешно запрошена\n')
            return src
    except:
        print('Start page return Error. Look at start_parce function')
        raise


# сохраняет стартовую страницу в html-файл, чтобы вдальнейшем обращаться к нему
def save_start_page(src):
    try:
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(src)
    except:
        print('Error in save_start_page function')
        raise


# чтение созданного html-файла и создание объекта суп
def read_start_page():
    try:
        with open('index.html', 'r', encoding='utf-8') as file:
            src = file.read()
            soup = BeautifulSoup(src, 'lxml')
        return soup
    except:
        print('Error in read_start_page function')
        raise


# сохранение таблицы со ссылками
def save_csv(link_list, prepath=''):
    try:
        with open(prepath + 'job_links_list.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(link_list)
    except:
        print('Error in save_csv function')
        raise

    # ссылка на стартовую страницу


# адреса парсеруемого сайта
url = 'https://www.weblancer.net/jobs/'
parent_url = 'https://www.weblancer.net'

pages = 1

# перебираем все страницы с выдачей результатов
all_jobs = []
for page in range(1, pages + 1):
    # загрузка страницы
    src = start_parce(url, params={'page': page}, test_print=True)
    # сохранение её в html и создаём суп
    save_start_page(src)
    soup = read_start_page()
    # вытаскиваем ссылки на все вакансии страницы
    job_list = soup.find_all('div', class_='row click_container-link set_href')
    job_count = 1
    # перебираем все вакансии на текущей странице
    for job in job_list:
        # делаем проверику сбора данных
        try:
            # проверка открыта ли вакансия
            if not (soup.find('span', text='Завершен') or soup.find('span', text='Закрыт')):
                job_link = parent_url + job.find('div', class_='title').find('a').get('href')
                all_jobs.append([job_link])
        # и при ошибке выводим номер страницы и номер вакансии
        except:
            print(f'Error. Last sucsessful operation on job_count - {job_count}, page - {page}')
        print(f'Progress of parcing job links: {job_count} on {page}/{pages} pages')
        job_count += 1
    # имитируем работу человека
    sleep(random.randrange(2, 3))

# сохраняем ссылки в таблицу
save_csv(all_jobs)

link_count = 1
# проверяем текст каждой ссылки, ищем в нём интересные нам вакансии
with open('job_links_list.csv', 'r', encoding='utf-8') as file:
    job_text_list = []
    try:
        for link in file:
            # загрузка страницы
            resp_text = start_parce(link, test_print=True)
            # сохранение её в html и создаём суп
            try:
                # запрос сохраняем в html
                with open(f'data/{link_count}_job.html', 'w', encoding='utf-8') as file:
                    file.write(resp_text)
            except:
                print('Error save vacancy in html')
                raise

            # создаём из него суп
            try:
                with open(f'data/{link_count}_job.html', 'r', encoding='utf-8') as file:
                    src = file.read()
                    soup = BeautifulSoup(src, 'lxml')
            except:
                print('Error read vacancy from html')
                raise

            job_text = soup.find('p').get_text(strip=True)
            # проверяем ключевые слова в заголовки
            for word in job_word_keys:
                if word in job_text:
                    job_name = soup.find('h1').get_text(strip=True)
                    job_link = link
                    job_text_list.append([job_name, job_text, job_link])
            link_count += 1
            sleep(random.randrange(2, 4))
    except:
        print(f'Truble with read job_links_list.csv in {link_count} link count')
save_csv(job_text_list, prepath='data/')

# finish words
print('All script made sucsessful')
