from random import randrange
import requests
from datetime import datetime
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import Vk
import db


def user_search(sex, city, min_age, max_age, relation, cont):
    """Логика поиска пользователя"""
    
    string = ''
    while True:
        if db.search(sex, city, min_age, max_age, relation):
            acc = db.search(sex, city, min_age, max_age, relation)
            string1 = f'https://vk.com/id{acc[1]}\n'
            string2 = '\n'.join([str(item) for item in vk.get_photos(requests, str(acc[1]))])
            string = string1 + string2 
            if vk.get_photos(requests, str(acc[1])):
                db.mark_shown(acc[1],)
                break
            else:
                db.mark_shown(acc[1],)
               
        else:
            print('Больше нет пользователей, удовлетворяющих условиям')
            string = 'Больше нет пользователей, удовлетворяющих условиям'
            break
    
    return string


def write_msg(user_id, message):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


if __name__ == '__main__':

    token = '70faa59071cc0ebdbedf03e4658daad3144e316765fad9dccb5c8df2e55746169d4df3b24b838fb1d8834'
    token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

    vk = Vk.VkUser(token_vk)
    users = vk.get_users()

    db = db.Db('users.db')
    db.create()
    db.add(users)

    print('Далее продолжайте общение с ботом vk. Введите "Старт" для начала.')

    vk_bot = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk_bot)
    

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text == 'Старт':
            
            write_msg(event.user_id, "Искать по данным Вашего аккаунта? (Да/Нет/Выход)")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text == 'Да':
                    
                    account = vk.get_user_data(event.user_id)
                    if 'city' in account:
                        city = account['city']['title']
                    else:
                        for event in longpoll.listen():
                            write_msg(event.user_id, "Введите город")
                            if event.type == VkEventType.MESSAGE_NEW:
                                if event.to_me:
                                    city = event.text
                                    break
                    if 'sex' in account:
                        sex = abs(account['sex'] - 1)
                    else:
                        write_msg(event.user_id, "Введите пол. 1 - женский, 2 - мужской")
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW:
                                if event.to_me:
                                    sex = event.text
                                    break
                    
                    if 'bdate' in account:
                        bdate_list = account['bdate'].split('.')
                        bdate = datetime.strptime(bdate_list[2] + bdate_list[1] + bdate_list[0], '%Y%m%d')
                        age = (datetime.now() - bdate).days//365.25
                    else:
                        write_msg(event.user_id, 'Введите свой возраст')
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW:
                                if event.to_me:
                                    age = int(event.text)
                                    break

                    min_age = age - 5
                    max_age = age + 5
                    relation = '4'
                    cont = 'Да'
                    write_msg(event.user_id, user_search(sex, city, min_age, max_age, relation, cont))
                    write_msg(event.user_id, "Следующая страница? (Да/Нет)")
                    
                    for event1 in longpoll.listen():
                        
                        if event1.type == VkEventType.MESSAGE_NEW and event1.to_me and event1.text == 'Да':
                            
                            write_msg(event.user_id, user_search(sex, city, min_age, max_age, relation, cont))
                            write_msg(event.user_id, "Следующая страница? (Да/Нет)")
                            if event1.to_me:
                                cont = event1.text
                        
                        if event1.type == VkEventType.MESSAGE_NEW and event1.to_me and event1.text == 'Нет':
                            write_msg(event.user_id, "Искать по данным Вашего аккаунта? (Да/Нет/Выход)")
                            break

                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text == 'Нет':
                    write_msg(event.user_id, "Введите город")
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                            city = event.text
                            break
                    write_msg(event.user_id, "Введите пол. 1 - женский, 2 - мужской")
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                            sex = event.text
                            break
                    write_msg(event.user_id, "Введите минимальный возраст")
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                            min_age = int(event.text)
                            break
                    write_msg(event.user_id, "Введите максимальный возраст")
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                            max_age = int(event.text)
                            break
                    relation = '4'
                    cont = 'Да'
                    message = user_search(sex, city, min_age, max_age, relation, cont)
                    write_msg(event.user_id, message)
                    if message != 'Больше нет пользователей, удовлетворяющих условиям':
                        write_msg(event.user_id, "Следующая страница? (Да/Нет)")
                        
                        for event1 in longpoll.listen():
                            
                            if event1.type == VkEventType.MESSAGE_NEW and event1.to_me and event1.text == 'Да':
                                
                                message = user_search(sex, city, min_age, max_age, relation, cont)
                                write_msg(event.user_id, message)
                                if message != 'Больше нет пользователей, удовлетворяющих условиям':
                                    write_msg(event.user_id, "Следующая страница? (Да/Нет)")
                                    if event1.to_me:
                                        cont = event1.text
                                else:
                                    write_msg(event.user_id, "Искать по данным Вашего аккаунта? (Да/Нет/Выход)")
                            
                            if event1.type == VkEventType.MESSAGE_NEW and event1.to_me and event1.text == 'Нет':
                                write_msg(event.user_id, "Искать по данным Вашего аккаунта? (Да/Нет/Выход)")
                                break
                    else:
                        write_msg(event.user_id, "Искать по данным Вашего аккаунта? (Да/Нет/Выход)")

                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text == 'Выход':
                    write_msg(event.user_id, "Работа чат-бота завершена.")
                    break
            break
