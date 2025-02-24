# Standard library imports
import time
import asyncio

# Third party imports
import requests
import re
import ssl
from urllib3 import poolmanager
from bs4 import BeautifulSoup as BS

#SQL Alchemy
from sqlalchemy.sql.expression import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete

# Local application imports
from database.models import (
    BishkekVacancy,
    engine,
    insert
)
from configs.constants import BISHKEK_SCRAPER_URL as url



class TLSAdapter(requests.adapters.HTTPAdapter):
    """
    Этот класс отвечает за обхождение SSL-защиты job.kg
    Тут лучше ничего не трогать, вряд-ли сломается
    """
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx)


session = requests.session()
session.mount('https://', TLSAdapter())


class Scraper:
    """
    Этот класс отвечает за парсинг информации
    """
    def __init__(self, url):
        """
        Константин сказал написать доки ко ВСЕМУ, поэтому...
        Инициализация класса...(-_-')
        """
        main_html = self.get_html(url)
        self.soup = BS(main_html, 'html.parser')

    def get_html(self, url) -> str:
        """
        Функция, отвечающая за get-запросы
        """
        r = session.get(url)
        if r.status_code == 200:
            return r.text
        elif r.status_code == 403:
            print('Вы заблокированы на этом сайте!')
            return 0
        elif r.status_code == 404:
            print('Страница не найдена!')
            return 0

    def get_amount_of_pages(self) -> int:
        """
        Эта функция возвращает общее количество страниц
        """
        amount_of_pages = self.soup.find_all('a', class_='lb-orange-item page')
        max_page = int(max([i.text for i in amount_of_pages]))
        return max_page

    def get_headers(self, content) -> list:
        """
        Эта функция возвращает заголовки вакансий
        """
        headers = content.find_all('a', class_="title-")
        return [i.text for i in headers]

    def get_links(self, content):
        """
        Эта функция возвращает уникальные фрагменты ссылки на подробное описание каждой вакансии
        """
        descriptions = [i['href']
                        for i in content.find_all('a', class_='title-')]
        return descriptions

    def get_adresses(self, content) -> list:
        """
        Эта функция возвращает регион работы
        """
        adresses = content.find_all('b', class_="address-")
        return [i.text.replace('\xa0', ' ') for i in adresses]

    def get_salary(self, content) -> str:
        """
        Зарплата
        """
        salaryes = content.find_all('b', class_="salary-")
        return [i.text.replace('\xa0', ' ') for i in salaryes]

    def get_description(self, content) -> str:
        """
        Описание вакансии
        """
        try:
            return content.find(
                'div', class_="details-").text.replace('\xa0', ' ').replace('\r', '').split('\n\n\n\n')[1].strip()
        except:
            return content.find(
                'div', class_="details-").text.replace('\xa0', ' ').replace('\r', '').strip()

    def get_company_name(self, content) -> str:
        """
        Названия лица-работодателя
        """
        if content.find('div', class_="employer- clearfix").p.b.a:
            return content.find('div', class_="employer- clearfix").p.b.a.text
        else:
            return content.find('div', class_="employer- clearfix").p.b.text

    def get_required_experience(self, content) -> str:
        """
        Эта функция возвращает требуемый для вакансии опыт работы
        """
        if "Опыт" in content:
            return content[content.index("Опыт")+2]
        else:
            return 'не требуется.'

    def get_schedule(self, content) -> str:
        """
        Эта функция возвращает график работы
        """
        if "График" in content:
            return content[content.index("График")+2]
        else:
            return 'Свободный график'


class Filler(Scraper):
    """
    Это класс отвечает за приготовление информации для сохранения в БД
    и непосредственно за сохранение в БД
    (БД -- База Данных)
    """
    def __init__(self, url):
        """
        Константин сказал написать доки ко ВСЕМУ, поэтому...
        Инициализация класса...(-_-')
        """
        Scraper.__init__(self, url)

    def get_data(self):
        """
        Сбор информации в специальную структуру для последующего сохранения в БД
        (БД -- База Данных)
        """
        data = []
        for page in range(1, self.get_amount_of_pages() + 1):
            soup = BS(self.get_html(
                f'https://www.job.kg/it-work?page={page}'), 'html.parser')
            links = [f'https://www.job.kg{url}' for url in self.get_links(soup)]
            adresses = self.get_adresses(soup)
            headers = self.get_headers(soup)
            salaryes = self.get_salary(soup)
            descriptions = []
            company_names = []
            experience = []

            schedule = []
            for url in details:
                detail_soup = BS(self.get_html(
                    f'https://www.job.kg{url}'), 'html.parser')
                try:
                    descriptions.append(detail_soup.find(
                        'div', class_="details-").text.replace('\xa0', ' ').split('\n\n\n\n')[1].strip())
                except:
                    descriptions.append(detail_soup.find(
                        'div', class_="details-").text.replace('\xa0', ' ').strip())
                try:
                    company_names.append(detail_soup.find(
                        'div', class_="employer- clearfix").p.b.a.text)
                except AttributeError:
                    company_names.append(detail_soup.find(
                        'div', class_="employer- clearfix").p.b.text)

                elements_of_kasha = re.split(
                    '<dt>|</dt>|<dd>|</dd>', str(detail_soup.find('div', class_="vvloa-box").dl))
                descriptions.append(self.get_description(detail_soup))
                company_names.append(self.get_company_name(detail_soup))
                experience.append(
                    self.get_required_experience(elements_of_kasha))
                schedules.append(self.get_schedule(elements_of_kasha))
            for index in range(len(adresses)):
                if adresses[index] == 'Кыргызстан: · Бишкек':
                    data.append((headers[index], company_names[index], experience[index],
                                 salaryes[index], schedules[index], descriptions[index], links[index]))
        return data

    async def filling_database(self):
        """
        Сохранение в БД.
        (БД -- База Данных)
        """
        async with engine.begin() as connection:
            cmd = delete(BishkekVacancy)
            await connection.execute(cmd)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            async with session.begin():
                for data in self.get_data():
                    if 'python' in data[5] or 'Python' in data[5]:
                        add_vacancy = insert(BishkekVacancy).values(
                            {
                                'header': data[0],
                                'company_name': data[1],
                                'required_experience': data[2],
                                'salary': data[3],
                                'schedule': data[4],
                                'details': data[5],
                                'link': data[6],
                                'type': 'Python'
                            }
                        )
                        await session.execute(add_vacancy)
                    elif 'javascript' in data[5] or 'JavaScript' in data[5] in data[5]:
                        add_vacancy = insert(BishkekVacancy).values(
                            {
                                'header': data[0],
                                'company_name': data[1],
                                'required_experience': data[2],
                                'salary': data[3],
                                'schedule': data[4],
                                'details': data[5],
                                'type': 'JavaScript'
                            }
                        )
                        await session.execute(add_vacancy)
        await session.commit()
        return 'Good job!'


if __name__ == "__main__":
    scraper = Scraper(url)
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(filling_database(scraper))
        time.sleep(3000)

