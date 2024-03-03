from Vk.vk_apis import VK_API_Client
from Yandex_Disk.yandex_disk_api import Yandex_Disk_API_Client
from tqdm import tqdm
import time
import os
import configparser

# Функция для проверки наличия файла config.ini
def check_config_exists():
    return os.path.exists('config.ini')

# Функция для чтения user_id и token_yandex из config.ini
def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['USER_VK']['user_id'], config['YANDEX']['token_yandex']

# Функция для записи user_id и token_yandex в config.ini
def write_config(user_id, token_yandex):
    config = configparser.ConfigParser()
    config['USER_VK'] = {'user_id': user_id}
    config['YANDEX'] = {'token_yandex': token_yandex}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def backup():
    # Проверяем наличие файла config.ini
    if check_config_exists():
        use_saved_data = input('Хотите использовать ранее сохраненные данные? (yes/no): ').lower()
        if use_saved_data == 'yes':
            # Читаем user_id и token_yandex из config.ini
            user_id, token_yandex = read_config()
        else:
            # Запрашиваем у пользователя user_id и token_yandex
            user_id = input('Введите Ваш UserId: ')
            token_yandex = input('Введите Ваш токен Яндекс.Диска: ')
            # Записываем user_id и token_yandex в config.ini
            write_config(user_id, token_yandex)
    else:
        # Запрашиваем у пользователя user_id и token_yandex
        user_id = input('Введите Ваш UserId: ')
        token_yandex = input('Введите Ваш токен Яндекс.Диска: ')
        # Записываем user_id и token_yandex в config.ini
        write_config(user_id, token_yandex)

    print('Используется пользовательский ID:', user_id)
    print('Используется токен Яндекс.Диска:', token_yandex)

    def count_file_name_occurrences():
        file_name = "file_name"
        with open("logs/photos_info.json", "r") as file:
            return sum(line.count(file_name) for line in file)

    vk_client = VK_API_Client(user_id)
    yandex_disk_client = Yandex_Disk_API_Client(token_yandex)

    print('Загрузка фотографий из VK...')
    vk_client.get_photo()
    print('Загрузка фотографий завершена.')

    print('Загрузка фотографий на Яндекс.Диск...')
    yandex_disk_client.save_photo()
    print('Загрузка фотографий на Яндекс.Диск завершена.')

    # Определяем количество загруженных фотографий для прогресс-бара
    occurrences = count_file_name_occurrences()

    # Имитируем прогресс-бар
    for _ in tqdm(range(occurrences), desc='Загрузка фото'):
        time.sleep(1)

    print('Загрузка фото завершена')

backup()
