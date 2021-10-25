import vk_api
import requests


class VkUser:
    """Работа с vk.com"""

    def __init__(self, token_vk):
        """Инициализация класса"""

        vk_session = vk_api.VkApi(token=token_vk)
        self.vk = vk_session.get_api()
        self.token_vk = token_vk

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
            'access_token': self.token_vk,
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