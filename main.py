from Vk.vk_apis import VK_API_Client
from Yandex_Disk.yandex_disk_api import Yandex_Disk_API_Client
from tqdm import tqdm
import time

def backup(user_id, token_yandex):
    
    def count_file_name_occurrences():
        file_name = "file_name"
        with open("logs/photos_info.json", "r") as file:
            return sum(line.count(file_name) for line in file)

    vk_client = VK_API_Client(user_id)
    yandex_disk_client = Yandex_Disk_API_Client(token_yandex)

    vk_client.get_photo()
    yandex_disk_client.save_photo()
    
    occurrences = count_file_name_occurrences()
    for _ in tqdm(range(occurrences), desc='Загрузка фото'):
        time.sleep(1)

    print('Загрузка фото завершена')

    
backup(user_id = input('Введите Ваш UserId: '), token_yandex = input('Введите Ваш токен Яндекс.Диска: '))
