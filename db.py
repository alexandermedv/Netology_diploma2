import sqlite3
import json


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