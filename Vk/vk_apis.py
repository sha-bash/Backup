import requests
import json
import pprint
from datetime import datetime


class VK_API_Client:
    SERVICE_TOKEN = 'Сервисный токен'
    API_BASE_URL = 'https://api.vk.com/method/'
    API_VERSION = '5.131'
    
    def __init__(self, user_id): 
        self.user_id = user_id    
        
    def _get_common_params(self):
        return {
           'access_token': self.SERVICE_TOKEN,
           'v': self.API_VERSION 
        }
        
    def _build_reqwest(self, api_methot):
        return f'{self.API_BASE_URL}/{api_methot}'
    
    def get_photo(self):
        params = self._get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': '1', 'photo_sizes': '1'})
        response = requests.get(self._build_reqwest('photos.get'), params=params)
        if response.status_code == 200:
            photos_data = []
            data = response.json().get('response', {}).get('items', [])
            for item in data:
                photo_info = {
                    'likes': item.get('likes', {}).get('count', ''),
                    'date': item.get('date', 0),
                    'type': item.get('sizes', [])[0].get('type', ''),
                    'url': item.get('sizes', [])[0].get('url', '')
                }
                photos_data.append(photo_info)
            with open('VK/photos_data.json', 'w') as json_file:
                json.dump(photos_data, json_file, ensure_ascii=False, indent=4)
            self._log_action(f'Фото профиля')
            return json_file 
        else:
            return f"Ошибка: {response.status_code}"
        
    def get_max_size_photo(self):
        params = self._get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': '1', 'photo_sizes': '1'})
        response = requests.get(self._build_reqwest('photos.get'), params=params)
        if response.status_code == 200:
            photos_data = []
            data = response.json().get('response', {}).get('items', [])
            max_size_photo = {}
            for item in data:
                photo_info = {
                    'likes': item.get('likes', {}).get('count', ''),
                    'date': item.get('date', 0),
                    'type': item.get('sizes', [])[0].get('type', ''),
                    'url': item.get('sizes', [])[0].get('url', '')
                }
                photos_data.append(photo_info)
                max_size = 0
                photos_info = {}
                for size in item['sizes']:
                    if size['height'] >= max_size:
                        max_size = size['height']
                if photo_info['likes'] not in max_size_photo.keys():
                    max_size_photo[photo_info['likes']] = photo_info['url']
                    photos_info['file_name'] = f"{photo_info['likes']}.jpg"
                else:
                    max_size_photo[f"{photo_info['likes']} + {photo_info['date']}"] = photo_info['url']
                    photos_info['file_name'] = f"{photo_info['likes']}+{photo_info['date']}.jpg"
        with open('VK/photos_data_max_size.json', 'w') as json_file:
            json.dump(photos_data, json_file, ensure_ascii=False, indent=4)
        return json_file


    def _log_action(self, action):
        with open('logs/vk_log.txt', 'a', encoding='UTF-8') as logfile:
            logfile.write('{} {}: загрузка завершена\n'.format(datetime.now().strftime('%d.%m.%Y %H:%M'), action))


if __name__ == '__main__':
    vk_client = VK_API_Client('Ваш user_id')
    pprint.pprint(vk_client.get_photo())