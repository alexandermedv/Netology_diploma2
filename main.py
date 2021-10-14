from random import randrange
import requests
import os
import json
import time
from datetime import datetime

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlite3
from pprint import pprint


class VkUser:
    """Работа с vk.com"""

    def __init__(self, token_vk):
        """Инициализация класса"""

        vk_session = vk_api.VkApi(token=token_vk)
        self.vk = vk_session.get_api()

    def get_users(self):
        """Получение списка пользователей"""
        self.users = self.vk.users.search(count=1000, relation=['1','6'], fields=['sex', 'bdate', 'city', 'relation'])

        return self.users

    def get_user_data(self, id):
        """Получение данных выбранного пользователя"""

        user = self.vk.users.get(user_id=id, fields = ['sex, bdate, city, status'])

        return user[0]

    def get_photos(self, q, id):
        """Получение фотографий с vk.com"""
        self.params = {
            'access_token': token_vk,
            'v': '5.131'
        }
        photos_get_params = {
            'owner_id': id,
            'album_id': 'profile',
            'extended': '1'
        }
        req = requests.get('https://api.vk.com/method/photos.get', params={**self.params, **photos_get_params}).json()

        photo_list = []
        if 'response' in req:
            for photo in req['response']['items']:
                likes = photo['likes']['count']
                comments = photo['comments']['count']
                likes_comments = likes + comments
                url = photo['sizes'][-1]['url']
                photo_list.append({'likes_comments': likes_comments, 'url': url})

        photo_list_sorted = sorted(photo_list, key=lambda d: d['likes_comments'], reverse=True)

        result = []
        for photo in photo_list_sorted[:3]:
            result.append(photo['url'])

        return result


class Db:
    """Работа с базой данных"""

    def __init__(self, path):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect(path)

    def create(self):
        """Создание базы данных и таблицы с аккаунтами"""

        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            first_name text,
            id integer,
            sex integer,
            bdate text,
            bdate_string text,
            bdate_formatted text,
            age integer,
            city_id integer,
            city_name text,
            relation text,
            shown integer,
            result dict);
            """)
        cur.execute("""DELETE FROM users""")
        self.conn.commit()
        print('База данных создана')

    def add(self, users):
        """Добавление пользователей из vk в нашу базу"""

        cur = self.conn.cursor()
        for user in users['items']:
            if 'first_name' in user:
                user_first_name = user['first_name']
            if 'id' in user:
                user_id = user['id']
            if 'sex' in user:
                user_sex = user['sex']
            if 'bdate' in user:
                user_bdate = user['bdate']
            if 'city' in user:
                user_city_id = user['city']['id']
                user_city_name = user['city']['title']
            else:
                user_city_id = ''
                user_city_name = ''
            if 'relation' in user:
                user_relation = user['relation']
            else:
                user_relation = ''

            cur.execute("""INSERT INTO users(
                first_name, 
                id, 
                sex, 
                bdate, 
                bdate_string,
                bdate_formatted,
                age,
                city_id, 
                city_name, 
                relation, 
                result) 
                VALUES(?,?,?,?,?,?,?,?,?,?,?);"""
                , (user_first_name, 
                user_id, 
                user_sex, 
                user_bdate, 
                None,
                None,
                None,
                user_city_id, 
                user_city_name, 
                user_relation, 
                json.dumps(user)
                ,) )
            cur.execute("""
                UPDATE users
                SET bdate_string = 
                    substr(bdate, -4)||
                    CASE length(substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1))
                        WHEN 1 THEN '0'||substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1)
                        WHEN 2 THEN substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1)
                    END
                    ||
                    CASE length(substr(bdate, 0, instr(bdate, '.')))
                        WHEN 1 THEN '0'||substr(bdate, 0, instr(bdate, '.'))
                        WHEN 2 THEN substr(bdate, 0, instr(bdate, '.'))
                    END
            """)
            cur.execute("""
                UPDATE users
                SET bdate_formatted = 
                    substr(bdate, -4)||'-'||
                    CASE length(substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1))
                        WHEN 1 THEN '0'||substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1)
                        WHEN 2 THEN substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1)
                    END
                    ||'-'||
                    CASE length(substr(bdate, 0, instr(bdate, '.')))
                        WHEN 1 THEN '0'||substr(bdate, 0, instr(bdate, '.'))
                        WHEN 2 THEN substr(bdate, 0, instr(bdate, '.'))
                    END
            """)
            cur.execute("""
                UPDATE users
                SET age = 
                    round((julianday('now') - julianday(substr(bdate, -4)||'-'||
                    CASE length(substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1))
                        WHEN 1 THEN '0'||substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1)
                        WHEN 2 THEN substr(substr(bdate, 0, length(bdate) - 4), instr(substr(bdate, 0, length(bdate) - 4), '.') + 1)
                    END
                    ||'-'||
                    CASE length(substr(bdate, 0, instr(bdate, '.')))
                        WHEN 1 THEN '0'||substr(bdate, 0, instr(bdate, '.'))
                        WHEN 2 THEN substr(bdate, 0, instr(bdate, '.'))
                    END))/365.25, 0)
            """)
        self.conn.commit()
        print('Пользователи добавлены в базу данных')

    def search(self, sex, city, min_age, max_age, relation):
        """Поиск пользователя в нашей базе"""

        bdate = ''
        cur = self.conn.cursor()
        cur.execute("""SELECT * 
        FROM users 
        WHERE sex = ?
            AND city_name = ?
            AND substr(bdate, -5, 1) = '.'
            AND shown is null
            AND age between ? and ?
            AND relation <> ?
            """, (sex, city, min_age, max_age, relation)
            
            )
        result = cur.fetchone()
        self.conn.commit()

        return result

    def mark_shown(self, id):
        """Отметка для просмотренных пользователей"""

        cur = self.conn.cursor()
        cur.execute("""UPDATE users
            SET shown = 1
            WHERE id = ?""", (id,))

        self.conn.commit()


def user_search(sex, city, min_age, max_age, relation, cont):
    """Логика поиска пользователя"""
    while True:
        if cont == 'Да':
            if db.search(sex, city, min_age, max_age, relation):
                acc = db.search(sex, city, min_age, max_age, relation)
                if vk.get_photos(requests, str(acc[1])):
                    print(f'https://vk.com/id{acc[1]}')
                    print(vk.get_photos(requests, str(acc[1])))
                    db.mark_shown(acc[1],)
                    
                else:
                    db.mark_shown(acc[1],)
            else:
                print('Больше нет пользователей, удовлетворяющих условиям')

            cont = input('Следующая страница? (Да/Нет)\n')
        elif cont == 'Нет':
            break
        else:
            print("Выберите 'Да' или 'Нет'")
            cont = input('Следующая страница? (Да/Нет)\n')


if __name__ == '__main__':

    token_vk = input('Введите токен\n')
    client_user_id = input('Введите ваш user_id\n')

    vk = VkUser(token_vk)
    users = vk.get_users()

    db = Db('users.db')
    db.create()
    db.add(users)

    while True:
        choice = input('Искать по данным Вашего аккаунта? (Да/Нет/Выход)\n')
        if choice == 'Да':
            account = vk.get_user_data(client_user_id)
            if account['city']:
                city = account['city']['title']
            else:
                city = input('Введите город\n')
            if account['sex']:
                sex = abs(account['sex'] - 1)
            else:
                while not (sex == '1' or sex == '2'):
                    sex = input('Введите пол. 1 - женский, 2 - мужской\n')
            
            if account['bdate']:
                bdate_list = account['bdate'].split('.')
                bdate = datetime.strptime(bdate_list[2] + bdate_list[1] + bdate_list[0], '%Y%m%d')
                age = (datetime.now() - bdate).days//365.25
            else:
                age = int(input('Введите свой возраст'))

            min_age = age - 5
            max_age = age + 5
            relation = '4'
            cont = 'Да'

            user_search(sex, city, min_age, max_age, relation, cont)
    
        elif choice == 'Нет':
            while True:
                sex = input('Введите пол. 1 - женский, 2 - мужской\n')
                if sex == '1' or sex == '2':
                    sex = int(sex)
                    break
            city = input('Введите город\n')
            min_age = input('Введите минимальный возраст\n')
            max_age = input('Введите максимальный возраст\n')
            relation = '4'
            cont = 'Да'
            user_search(sex, city, min_age, max_age, relation, cont)

        elif choice == 'Выход':
            break 
            
        else:
            print("Выберите 'Да', 'Нет' или 'Выход'")
