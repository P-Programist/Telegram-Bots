import asyncio
import requests
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete
from bs4 import BeautifulSoup as BS
from database.models import (
    WorldVacancy,
    engine,
    insert
)


class Scraper:
    """
    Этот класс отвечает за парсинг информации
    """
    def __init__(self):
        """
        Константин сказал написать доки ко ВСЕМУ, поэтому...
        Инициализация класса...(-_-')
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
            'From': 'mysupercoolemail@gmail.com'
        }

    def get_html(self, url):
        """
        Функция, отвечающая за get-запросы
        """
        time.sleep(10)
        print(f'Scraping from {url}...')
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            return r.text
        elif r.status_code == 403:
            print('Вы заблокированы на этом сайте!')
            return 0
        elif r.status_code == 404:
            print('Страница не найдена!')
            return 0

    def get_headers(self, content):
        """
        Эта функция возвращает заголовки вакансий
        """
        headers = content.find_all('up-c-line-clamp', lines='2')
        headers = [header.text for header in headers]
        return headers

    def get_details(self, content):
        """
        Эта функция возвращает уникальные ссылки на подробное описание каждой вакансии
        """
        links = content.find_all('a', class_="job-title-link break visited")
        links = [f"details/~{link['href'].split('~')[1]}" for link in links]
        return links

    def get_prices(self, content):
        """
        Плата за проект
        """
        prices = content.find_all('strong', class_="js-budget")
        prices = [price.text.replace('\n', ' ').strip() for price in prices]
        return prices

    def get_descriptions(self, content):
        """
        Подробное описание проекта
        """
        descriptions = content.find_all('span', class_="js-description-text")
        descriptions = [description.text.replace('\n', ' ') for description in descriptions]
        return descriptions

    def get_post_times(self, content):
        """
        Время подачи проекта
        """
        times = content.find_all('time')
        times = [time['datetime'] for time in times]
        return times

    def get_tags(self, content):
        """
        Тэги проекта(Необходимые для выполнения навыки)
        """
        tags = [[i.text for i in BS(str(time), 'html.parser').find_all(
            'span', class_="o-tag-skill disabled")] for time in content.find_all('div', class_="js-skills skills")]
        return [' '.join(['#'+i.replace(' ', '') for i in tag]) for tag in tags]


class Filler(Scraper):
    """
    Это класс отвечает за приготовление информации для сохранения в БД
    и непосредственно за сохранение в БД
    (БД -- База Данных)
    """
    def __init__(self):
        """
        Константин сказал написать доки ко ВСЕМУ, поэтому...
        Инициализация класса...(-_-')
        """
        Scraper.__init__(self)

    async def filling_database(self):
        """
        Сбор информации в специальную структуру и сохранение в БД
        (БД -- База Данных)
        """
        async with engine.begin() as connection:
            cmd = delete(WorldVacancy)
            await connection.execute(cmd)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            async with session.begin():
                for language in ('Python', 'JavaScript', 'HTML'):
                    for page in range(1, 6):
                        soup = BS(self.get_html(f'https://www.upwork.com/ab/jobs/search/t/1/?amount=100-499,-17&contractor_tier=1,2&page={page}&payment_verified=1&q={language}&sort=recency'), 'html.parser')
                        data = (self.get_headers(soup), self.get_descriptions(soup), self.get_prices(soup), self.get_post_times(soup), self.get_tags(soup), tuple([f'https://www.upwork.com/ab/jobs/search/t/{page}/{link}?amount=100-499,-17&contractor_tier=1,2&payment_verified=1&q={language}&sort=recency' for link in self.get_details(soup)]))
                        for chunk in range(len(data[4])):
                            add_vacancy = insert(WorldVacancy).values(
                                {
                                    'header': data[0][chunk],
                                    'description': data[1][chunk],
                                    'price': data[2][chunk],
                                    'post_time': data[3][chunk],
                                    'tags': data[4][chunk],
                                    'link': data[5][chunk],
                                    'type': language
                                }
                            )
                            await session.execute(add_vacancy)
                    if language != 'HTML':
                        time.sleep(120)
        await session.commit()
        return 'Good job!'


filler = Filler()
asyncio.run(filler.filling_database())