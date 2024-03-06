import json
import pprint
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class VK_Authenticator:
    def __init__(self):
        self.client_id = '51857807'
        self.redirect_uri = 'https://example.com/callback'
        self.scope = 'photos'
        self.state = '123456'
        
        # Инициализация драйвера с использованием WebDriver Manager
        driver_path = ChromeDriverManager().install()
        self.driver = Chrome(service=ChromeService(executable_path=driver_path))
    
    def get_access_token(self):
        try:
            self.driver.maximize_window()
            auth_url = f'https://oauth.vk.com/authorize?client_id={self.client_id}&display=page&redirect_uri={self.redirect_uri}&scope={self.scope}&response_type=token&v=5.131&state={self.state}'
            self.driver.get(auth_url)
            
            # Ждем, пока пользователь авторизуется и будет перенаправлен на другую страницу
            WebDriverWait(self.driver, 60).until(EC.url_contains('example.com/callback'))

            # Парсим URL, чтобы получить параметры
            url = self.driver.current_url
            parsed_url = urlparse(url)
            fragment = parsed_url.fragment
            token_dict = parse_qs(fragment)

            # Извлекаем access_token из словаря параметров
            access_token = token_dict['access_token'][0]
            return access_token
            
        except Exception as ex:
            print(f"Произошла ошибка: {ex}")
        finally:
            self.driver.quit()
            
class VK_API_Client:
    authenticator = VK_Authenticator()
    access_token = authenticator.get_access_token()
    API_BASE_URL = 'https://api.vk.com/method/'
    API_VERSION = '5.131'
    LOG_FILE_PATH = 'logs/vk_log.txt'
    PHOTOS_DATA_FILE_PATH = 'logs/photos_data.json'
    
    def __init__(self, user_id): 
        self.user_id = user_id    
        
    def _get_common_params(self):
        return {
           'access_token': self.access_token,
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
    
    def get_photo(self, count=5):
        change_count_photo = input('Хотите указать количество фото для загрузки (По умолчанию 5)? (yes/no) ')
        if change_count_photo.lower() == 'yes':
            count = int(input('Введите число фото для загрузки: '))
                
        params = self._get_common_params()
        params.update({'owner_id': self.user_id, 
                       'album_id': 'profile', 
                       'extended': '1', 
                       'photo_sizes': '1', 
                       'count': count})
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
            return f'{count} фото загружено'
        except Exception as e:
            return f"Ошибка: {e}"

if __name__ == '__main__':
    vk_client = VK_API_Client('Ваш userid Вк')
    pprint.pprint(vk_client.get_photo())
