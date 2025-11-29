import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import json
import webbrowser

# Загрузка переменных из .env файла
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_EXPIRES_AT = os.getenv('ACCESS_TOKEN_EXPIRES_AT')

# Проверка наличия необходимых переменных
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    print('Ошибка: Пожалуйста, убедитесь, что CLIENT_ID, CLIENT_SECRET и REDIRECT_URI заданы в файле .env')
    exit()

# Функция для получения текущего времени в UTC
def current_time():
    return datetime.now(timezone.utc)

# Функция для получения нового access_token с использованием authorization_code
def get_access_token_from_code(code):
    token_url = 'https://hh.ru/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, data=token_data)
    if response.status_code == 200:
        token_info = response.json()
        return token_info
    else:
        print(f'Ошибка при получении токена доступа: {response.status_code}')
        print(response.text)
        exit()

# Функция для обновления access_token с использованием refresh_token
def refresh_access_token():
    token_url = 'https://hh.ru/oauth/token'
    token_data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(token_url, data=token_data)
    if response.status_code == 200:
        token_info = response.json()
        return token_info
    else:
        print(f'Ошибка при обновлении токена доступа: {response.status_code}')
        print(response.text)
        exit()

# Проверяем, требуется ли обновление access_token
def is_token_expired():
    if not ACCESS_TOKEN or not ACCESS_TOKEN_EXPIRES_AT:
        return True
    expires_at = datetime.strptime(ACCESS_TOKEN_EXPIRES_AT, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    return current_time() >= expires_at

# Функция для сохранения переменных в .env файл
def update_env_file(new_vars):
    with open('.env', 'r') as file:
        env_vars = file.readlines()

    with open('.env', 'w') as file:
        updated_keys = set(new_vars.keys())
        for line in env_vars:
            key = line.strip().split('=')[0]
            if key in updated_keys:
                continue  # Пропускаем переменные, которые будем обновлять
            file.write(line)
        for key, value in new_vars.items():
            file.write(f'{key}={value}\n')

# Если access_token истёк или отсутствует, обновляем его
if is_token_expired():
    if REFRESH_TOKEN:
        # Обновляем access_token с использованием refresh_token
        token_info = refresh_access_token()
        ACCESS_TOKEN = token_info['access_token']
        REFRESH_TOKEN = token_info.get('refresh_token', REFRESH_TOKEN)
        expires_in = token_info.get('expires_in', 3600)  # По умолчанию 1 час
        expires_at = current_time() + timedelta(seconds=expires_in)
        ACCESS_TOKEN_EXPIRES_AT = expires_at.strftime('%Y-%m-%d %H:%M:%S')

        # Обновляем переменные в .env файле
        update_env_file({
            'ACCESS_TOKEN': ACCESS_TOKEN,
            'REFRESH_TOKEN': REFRESH_TOKEN,
            'ACCESS_TOKEN_EXPIRES_AT': ACCESS_TOKEN_EXPIRES_AT
        })
        print('ACCESS_TOKEN обновлен и сохранен в .env файл')

    else:
        # Получаем authorization_code вручную
        print('Необходимо получить authorization_code для получения ACCESS_TOKEN')
        auth_url = f'https://hh.ru/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=employer'
        print(f'Откройте в браузере следующую ссылку и авторизуйтесь: {auth_url}')
        webbrowser.open(auth_url)
        authorization_code = input('После авторизации введите параметр "code" из адресной строки: ')

        # Получаем access_token и refresh_token
        token_info = get_access_token_from_code(authorization_code)
        ACCESS_TOKEN = token_info['access_token']
        REFRESH_TOKEN = token_info.get('refresh_token', '')
        expires_in = token_info.get('expires_in', 3600)  # По умолчанию 1 час
        expires_at = current_time() + timedelta(seconds=expires_in)
        ACCESS_TOKEN_EXPIRES_AT = expires_at.strftime('%Y-%m-%d %H:%M:%S')

        # Сохраняем переменные в .env файл
        update_env_file({
            'ACCESS_TOKEN': ACCESS_TOKEN,
            'REFRESH_TOKEN': REFRESH_TOKEN,
            'ACCESS_TOKEN_EXPIRES_AT': ACCESS_TOKEN_EXPIRES_AT
        })
        print('ACCESS_TOKEN и REFRESH_TOKEN сохранены в .env файл')

# Заголовки для запросов к API
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'User-Agent': 'Wendy 4.0/1.0 (shishenya.ya@professionals4-0.ru)',
    'Accept': 'application/json'
}

# Функция для получения информации о текущем пользователе
def get_current_user_info():
    url = 'https://api.hh.ru/me'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        print(f'Ошибка при получении информации о пользователе: {response.status_code}')
        print(response.text)
        exit()

# Получение информации о текущем пользователе
user_info = get_current_user_info()

# Добавляем отладочный вывод
print("Ответ от /me:", json.dumps(user_info, ensure_ascii=False, indent=4))

# Получение EMPLOYER_ID из информации о пользователе
employer = user_info.get('employer')
if employer and 'id' in employer:
    EMPLOYER_ID = employer['id']
    print(f'EMPLOYER_ID: {EMPLOYER_ID}')
else:
    print('Ошибка: Не удалось получить EMPLOYER_ID из информации о пользователе.')
    print("Полный ответ от /me:", json.dumps(user_info, ensure_ascii=False, indent=4))
    exit()

# Функция для получения списка менеджеров
def get_managers(employer_id):
    url = f'https://api.hh.ru/employers/{employer_id}/managers'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        managers_info = response.json()
        return managers_info.get('items', [])
    else:
        print(f'Ошибка при получении списка менеджеров: {response.status_code}')
        print(response.text)
        exit()

# Получение списка менеджеров
managers = get_managers(EMPLOYER_ID)

# Проверка наличия менеджеров
if not managers:
    print('Не найдено ни одного менеджера.')
    exit()

# Функция для получения лимитов просмотра резюме для менеджера
def get_resume_view_limits(employer_id, manager_id, locale='RU', host='hh.ru'):
    url = f'https://api.hh.ru/employers/{employer_id}/managers/{manager_id}/limits/resume'
    params = {
        'locale': locale,
        'host': host
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Ошибка при получении лимитов для менеджера (ID: {manager_id}): {response.status_code}')
        print(response.text)
        return None

# Получение текущей даты и времени для имени файла
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'manager_limits_{timestamp}.txt'

# Сбор данных о лимитах менеджеров
manager_limits = []

for manager in managers:
    manager_id = manager.get('id')
    manager_name = manager.get('full_name')
    if not manager_id:
        continue

    # Получаем лимиты просмотра резюме для менеджера
    limits = get_resume_view_limits(EMPLOYER_ID, manager_id)
    if limits:
        manager_limits.append({
            'manager_id': manager_id,
            'manager_name': manager_name,
            'limits': limits
        })

# Вывод и сохранение данных
if manager_limits:
    # Вывод в консоль
    for item in manager_limits:
        print(f"\nМенеджер: {item['manager_name']} (ID: {item['manager_id']})")
        print('Лимиты и использованные просмотры:')
        print(json.dumps(item['limits'], ensure_ascii=False, indent=4))

    # Сохранение в файл
    with open(filename, 'w', encoding='utf-8') as f:
        for item in manager_limits:
            f.write(f"Менеджер: {item['manager_name']} (ID: {item['manager_id']})\n")
            f.write('Лимиты и использованные просмотры:\n')
            f.write(json.dumps(item['limits'], ensure_ascii=False, indent=4))
            f.write('\n\n')
    print(f'\nДанные сохранены в файл {filename}')
else:
    print('Не удалось получить информацию о лимитах ни для одного менеджера.')
