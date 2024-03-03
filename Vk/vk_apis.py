import requests
import json
import pprint
from datetime import datetime


class VK_API_Client:
    SERVICE_TOKEN = 'Сервисный ключ доступа'
    API_BASE_URL = 'https://api.vk.com/method/'
    API_VERSION = '5.131'
    LOG_FILE_PATH = 'logs/vk_log.txt'
    PHOTOS_DATA_FILE_PATH = 'logs/photos_data.json'
    
    def __init__(self, user_id): 
        self.user_id = user_id    
        
    def _get_common_params(self):
        return {
           'access_token': self.SERVICE_TOKEN,
           'v': self.API_VERSION 
        }
        
    def _build_request_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'
    
    def _make_vk_api_request(self, method, params):
        response = requests.get(self._build_request_url(method), params=params)
        if response.status_code == 200:
            response_json = response.json()
            if 'error' in response_json:
                error_msg = response_json['error']['error_msg']
                raise ValueError(f"VK API Error: {error_msg}")
            return response_json
        else:
            response.raise_for_status()

    def _log_action(self, action):
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
        with open(self.LOG_FILE_PATH, 'a', encoding='UTF-8') as logfile:
            logfile.write(f'{timestamp} {action}: загрузка завершена\n')
    
    def _save_photos_data(self, photos_data):
        with open(self.PHOTOS_DATA_FILE_PATH, 'w') as json_file:
            json.dump(photos_data, json_file, ensure_ascii=False, indent=4)
    
    def get_photo(self):
        params = self._get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': '1', 'photo_sizes': '1'})
        try:
            response_json = self._make_vk_api_request('photos.get', params)
            photos_data = []
            items = response_json.get('response', {}).get('items', [])
            for item in items:
                date_time = datetime.fromtimestamp(item.get('date', 0))
                formatted_date = date_time.strftime('%Y-%m-%d')
                photo_info = {
                    'likes': item.get('likes', {}).get('count', ''),
                    'date': formatted_date,
                    'type': item.get('sizes', [])[0].get('type', ''),
                    'url': item.get('sizes', [])[0].get('url', '')
                }
                photos_data.append(photo_info)
            self._save_photos_data(photos_data)
            self._log_action('Фото профиля')
            return photos_data
        except Exception as e:
            return f"Ошибка: {e}"

if __name__ == '__main__':
    vk_client = VK_API_Client('userid')
    pprint.pprint(vk_client.get_photo())
