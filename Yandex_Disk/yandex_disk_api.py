import json
import os
import pprint
import requests


class Yandex_Disk_API_Client:
    API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk'
    token_yandex = 'ваш токен Яндекс'
    
    def __init__(self, token_yandex):      
        self.token = token_yandex
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
    
    def _build_request(self, resource_name):
        return f'{self.API_BASE_URL}/{resource_name}'
    
    def get_common_params(self):
        return {
           'path': 'Резервные копии фото из ВК' 
        }
        
    def create_folder(self):
        params = self.get_common_params()
        response = requests.put(self._build_request('resources'), headers=self.headers, params=params)
        url_backup_path = response.json().get('href')
        return url_backup_path

    def get_info(self):
        params = self.get_common_params()
        response = requests.get(self._build_request('resources'), headers=self.headers, params=params)
        backup_path = response.json().get('path')
        return backup_path
    
    def _generate_photo_name(self):
        with open('logs/photos_data.json', 'rb') as json_file:
            profile_photos_data = json.load(json_file)
        photo_names = []
        photo_urls =[]
        photo_types = []
        for photo_data in profile_photos_data:
            photo_name = f"{photo_data['likes']}_{photo_data['date']}.jpeg"
            photo_url = photo_data['url']
            photo_type = photo_data['type']
            photo_names.append(photo_name)
            photo_urls.append(photo_url)
            photo_types.append(photo_type)   
        return photo_names, photo_urls, photo_types
    
    def save_photo(self):
        # Проверяем существует ли папка, если нет - создаем
        folder_path = self.get_info()
        if not folder_path:
            folder_path = self.create_folder()

        headers = self.headers
        upload_response = None
        photos_info = []
        for photo_name, photo_url, photo_type in zip(*self._generate_photo_name()):
            # Скачиваем фото по URL и сохраняем с именем photo_name
            photo_response = requests.get(photo_url)
            with open(f'logs/temp/{photo_name}', 'wb') as file:
                file.write(photo_response.content)
        
            # Загружаем фото на Яндекс.Диск
            upload_params = {'path': f"{folder_path}/{photo_name}", 'overwrite': 'true'}
            #print("Параметры загрузки:", upload_params)  # Добавлено для отладки
            upload_response = requests.get(self._build_request('resources/upload'), headers=headers, params=upload_params)
            current_url_upload = upload_response.json().get('href')
            #print("Текущий URL загрузки:", current_url_upload)  # Добавлено для отладки
        
            with open(f'logs/temp/{photo_name}', 'rb') as uploaded_file:
                files = {'file': (f'logs/temp/{photo_name}', uploaded_file)}
                upload_response = requests.put(current_url_upload, files=files)
            photos_info.append({
                "file_name": photo_name,
                "size": photo_type,
            })

            # Сохраняем информацию о загруженных фотографиях в json-файл
            with open('logs/photos_info.json', 'w') as json_file:
                json.dump(photos_info, json_file, ensure_ascii=False, indent=4)
            
            if upload_response.status_code == 201:
                os.remove(f'logs/temp/{photo_name}')
        
        return 'Загрузка фотографий на Яндекс.Диск завершена.'
        

if __name__ == '__main__':
    client = Yandex_Disk_API_Client(Yandex_Disk_API_Client.token_yandex)
    pprint.pprint(client.save_photo())
