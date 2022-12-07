import re
from datetime import datetime as dt
import requests
from bs4 import BeautifulSoup
import calendar


# Prayer Times
def get_prayer_times(city, currentMonth, *currentDay):
    """Return the time of prayer for given date"""
    url = f'https://islom.uz/vaqtlar/{city}/{currentMonth}'

    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    body = soup.find('tbody')
    head = soup.find('thead')
    city = soup.find('div', class_='city_prayer_block').find('h2').text.split(' ')
    try:
        for data in currentDay:
            day = body.find_all('td')[(data - 1) * 9 + 1].text
            month = head.find_all('th')[1].text
            prayer_day = body.find_all('td')[(data - 1) * 9 + 2].text
            Fajr = body.find_all('td')[(data - 1) * 9 + 3].text
            Sunrise = body.find_all('td')[(data - 1) * 9 + 4].text
            Dhuhr = body.find_all('td')[(data - 1) * 9 + 5].text
            Asr = body.find_all('td')[(data - 1) * 9 + 6].text
            Maghrib = body.find_all('td')[(data - 1) * 9 + 7].text
            Isha = body.find_all('td')[(data - 1) * 9 + 8].text

            msg = f'🌏Минтақа: {city[2]}\n'
            msg += f'{day} {month.title()} {prayer_day}\n'
            msg += f'<strong>🌇Тонг(Саҳарлик) : {Fajr}</strong>\n'
            msg += f'Қуёш : {Sunrise}\n'
            msg += f'Пешин : {Dhuhr}\n'
            msg += f'Аср : {Asr}\n'
            msg += f'<strong>🌃Шом(Ифтор) : {Maghrib}</strong>\n'
            msg += f'Хуфтон : {Isha}\n'

            return msg
    except:
        return 'Маълумот топилмади!'


def today_times(city: int):
    try:
        date = dt.now()
        return get_prayer_times(city, date.month, date.day)
    except:
        return 'Бугунга вактларни топаолмадим!'


def tomorrow_times(city: int):
    try:
        date = dt.now()
        last_day = calendar.monthrange(date.year, date.month)
        if date.month == last_day[0] and date.day != last_day[1]:
            return get_prayer_times(city, date.month + 1, 1)
        else:
            return get_prayer_times(city, date.month, date.day + 1)
    except:
        return 'Ертанги вактларни топаолмадим!'


def get_location_id():
    url = f'https://islom.uz/'

    response = requests.get(url)
    html = BeautifulSoup(response.content, 'html.parser')

    for el in html.select('.custom-select > select'):
        region = el.select('option')

        region = [i.text for i in region]
        id = [i.get('value') for i in el.select('option')]

        id = list(map(int, id))

        location = (dict(zip(region, id)))

    return location


# Sub menu
def take_ablution():
    """Тахорат олиш тартиби"""
    cleaning_section = {}

    url = f'https://namoz.islom.uz/'

    response = requests.get(url)
    html = BeautifulSoup(response.content, 'html.parser')

    try:
        for el in html.select('main > section'):
            id = el.get('id')[-1]
            title = el.select('h2')[0].text
            img = url + el.select('img')[0].get('src')
            text = [item.text for item in el.select('p')]
            text = '\n'.join(text)

            cleaning_section[int(id)] = {
                'title': title,
                'img': img,
                'text': text
            }
        return cleaning_section
    except:
        return 'Тахорат олиш тартиби буйча хозерча малумот ёк'


def prayer_order():
    """Намоз ўқиш тартиби"""
    prayer_text_section = {}

    response = requests.get('https://namoz.islom.uz/namoz.html')
    html = BeautifulSoup(response.content, 'html.parser')

    try:
        for el in html.select('main > section'):
            id = el.get('id')[8:]
            title = el.select('h2')[0].text
            img = 'https://namoz.islom.uz/' + el.select('img')[0].get('src')
            text = [item.text for item in el.select('p')]
            text = '\n'.join(text)

            if el.select('.text__block'):
                translated_text = [item.text for item in el.select('.tarjima__text')]
                audio_text = [item.text for item in el.select('.audio__text')]
                arabic_text = [item.text for item in el.select('.arabic__text')]
                audio_text = '\n'.join(audio_text)
                translated_text = '\n'.join(translated_text)
                arabic_text = '\n'.join(arabic_text)
            else:
                audio_text = None
                translated_text = None
                arabic_text = None

            if el.select('audio > source'):
                mp3 = ['https://namoz.islom.uz/' + item.get('src')
                       for item in el.select('audio > source')]
            else:
                mp3 = None

            # print(f"{id} {mp3}")
            # print(type(audio_text))

            prayer_text_section[int(id)] = {
                'title': title,
                'img': img,
                'text': text,
                'audio_text': audio_text,
                # 'translated_text': translated_text,
                'arabic_text': arabic_text,
                'mp3': mp3,
            }

        return prayer_text_section
    except:
        return 'Намоз ўқиш тартиби хакида хозерча малумот ёк'


def surah_section(section_id: int) -> dict:
    surah_description = {}
    arabic_text = []
    surah_texts = []

    url = f'https://namoz.islom.uz/suralar.html'

    response = requests.get(url)
    html = BeautifulSoup(response.content, 'html.parser')

    try:
        for el in html.select(f'main > #section-{section_id}'):
            arabic = el.select('.arabic__text')[0].text.replace('\t', '').replace(' ', '').split('\n')
            title = el.select('h2')[0].text
            audio = 'https://namoz.islom.uz/' + el.select('source')[0].get('src')
            text = el.select('.tarjima__text')[0].text
            text = text.replace('\t', '').replace('\n', '').replace('  ', ' ')
            text = re.split(r'[(]?[\s][0-9]{1,2}[.][\s]', text)
            surah_texts.append(text[0])

            for numb, i in enumerate(text[1:]):
                surah_texts.append(f'{numb+1}. {i}')

            surah_description = {
                'title': title,
                'arabic': arabic,
                'audio': audio,
                'text': surah_texts
            }

        return surah_description
    except:
        return 'Айтилган сурангиз хакида хозерча малумот ёк'


def surah():
    surah_id = {}
    url = f'https://namoz.islom.uz/suralar.html'

    response = requests.get(url)
    html = BeautifulSoup(response.content, 'html.parser')

    for el in html.select('main > section'):
        id = el.get('id')[8:]
        title = el.select('h2')[0].text
        surah_id[title] = int(id)
    return surah_id


if __name__ == '__main__':
    pr=prayer_order()
    val_title = 0
    val_img = 0
    val_text = 0
    val_audio_text = 0
    val_arabic_text = 0
    val_mp3 = 0
    # print((pr.get(13).keys()))
    for numb in range(1, 14):
        i = pr.get(numb)
        if i['title']: val_title += 1
        if i['img']: val_img += 1
        if i['text']: val_text += 1
        if i['audio_text']: val_audio_text += 1
        if i['arabic_text']: val_arabic_text += 1
        if i['mp3']: val_mp3 += 1

    print(f'val_title={val_title}')
    print(f'val_img={val_img}')
    print(f'val_text={val_text}')
    print(f'val_audio_text={val_audio_text}')
    print(f'val_arabic_text={val_arabic_text}')
    print(f'val_mp3={val_mp3}')

