from Vk.vk_apis import VK_API_Client
from Yandex_Disk.yandex_disk_api import Yandex_Disk_API_Client
import tqdm
import time

def backup(user_id, token_yandex):
    vk_client = VK_API_Client(user_id)
    yandex_disk_client = Yandex_Disk_API_Client(token_yandex)

    vk_client.get_photo()
    yandex_disk_client.save_photo()
    for _ in tqdm(range(8), desc='Загрузка фото'):
        time.sleep(1)

    print('Загрузка фото завершена')

    
backup(user_id = input('Введите Ваш UserId: '), token_yandex = input('Введите Ваш токен Яндекс.Диска: '))
