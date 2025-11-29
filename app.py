import requests
import os
import re
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from flask import Flask, redirect, url_for, session, request, render_template, flash
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

# Настройки из .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SECRET_KEY = os.getenv('SECRET_KEY')
USER_AGENT = os.getenv('USER_AGENT', 'HH Limits/1.0')

# Константы
REQUEST_TIMEOUT = 10  # секунды

app.secret_key = SECRET_KEY
app.config['JSON_AS_ASCII'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Защита от XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF защита

# Проверка наличия обязательных настроек
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SECRET_KEY]):
    logger.error("Отсутствуют обязательные переменные окружения")
    raise Exception("Пожалуйста, убедитесь, что все обязательные переменные заданы в файле .env")

# Главная страница с кнопкой авторизации
@app.route('/')
def index():
    return render_template('index.html')

# Перенаправление на страницу авторизации HH.ru
@app.route('/login')
def login():
    auth_url = (
        f"https://hh.ru/oauth/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=employer"
    )
    return redirect(auth_url)

# Обработка обратного вызова от HH.ru
@app.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        flash(f"Ошибка авторизации: {error}", "danger")
        return redirect(url_for('index'))

    code = request.args.get('code')
    if not code:
        flash("Отсутствует параметр 'code' в запросе", "danger")
        return redirect(url_for('index'))

    # Валидация кода (только буквы и цифры)
    if not re.match(r'^[A-Za-z0-9_-]+$', code):
        logger.warning(f"Некорректный формат кода авторизации: {code[:10]}...")
        flash("Некорректный формат кода авторизации", "danger")
        return redirect(url_for('index'))

    # Обмен кода на токен
    token_url = 'https://hh.ru/oauth/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    try:
        response = requests.post(token_url, data=token_data, timeout=REQUEST_TIMEOUT)
    except requests.Timeout:
        logger.error("Timeout при получении токена")
        flash("Превышено время ожидания ответа от HH.ru. Попробуйте снова.", "danger")
        return redirect(url_for('index'))
    except requests.RequestException as e:
        logger.error(f"Ошибка сети при получении токена: {str(e)}")
        flash("Ошибка соединения с HH.ru. Попробуйте позже.", "danger")
        return redirect(url_for('index'))
    if response.status_code != 200:
        flash(f"Ошибка при получении токена доступа: {response.status_code}\n{response.text}", "danger")
        return redirect(url_for('index'))

    token_info = response.json()
    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')
    expires_in = token_info.get('expires_in', 3600)  # По умолчанию 1 час
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    if not access_token or not refresh_token:
        flash("Не удалось получить access_token или refresh_token", "danger")
        return redirect(url_for('index'))

    # Сохранение токенов в сессии
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    session['expires_at'] = expires_at.strftime('%Y-%m-%d %H:%M:%S')

    flash("Авторизация прошла успешно!", "success")
    return redirect(url_for('limits'))

# Функция для обновления access_token с использованием refresh_token
def refresh_access_token(refresh_token):
    token_url = 'https://hh.ru/oauth/token'
    token_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    try:
        response = requests.post(token_url, data=token_data, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ошибка при обновлении токена доступа: {response.status_code}\n{response.text}")
    except requests.Timeout:
        logger.error("Timeout при обновлении токена")
        raise Exception("Превышено время ожидания ответа от HH.ru")
    except requests.RequestException as e:
        logger.error(f"Ошибка сети при обновлении токена: {str(e)}")
        raise Exception(f"Ошибка соединения с HH.ru: {str(e)}")

# Проверка и обновление токена
def get_valid_access_token():
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    expires_at_str = session.get('expires_at')

    if not access_token or not refresh_token or not expires_at_str:
        raise Exception("Токены отсутствуют. Пожалуйста, авторизуйтесь снова.")

    expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) >= expires_at:
        # Токен истёк, обновляем
        try:
            token_info = refresh_access_token(refresh_token)
            access_token = token_info['access_token']
            refresh_token = token_info.get('refresh_token', refresh_token)
            expires_in = token_info.get('expires_in', 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            # Обновление сессии
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            session['expires_at'] = expires_at.strftime('%Y-%m-%d %H:%M:%S')

        except Exception as e:
            raise Exception(f"Не удалось обновить токен доступа: {str(e)}")

    return access_token

# Функция для получения информации о менеджере
def get_manager_info(employer_id, manager_id, headers):
    url = f'https://api.hh.ru/employers/{employer_id}/managers/{manager_id}'
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Ошибка при получении информации о менеджере (ID: {manager_id}): {response.status_code}")
            return None
    except requests.Timeout:
        logger.error(f"Timeout при получении информации о менеджере (ID: {manager_id})")
        return None
    except requests.RequestException as e:
        logger.error(f"Ошибка сети при получении информации о менеджере: {str(e)}")
        return None

# Функция для получения лимитов просмотра резюме для менеджера
def get_resume_view_limits(employer_id, manager_id, headers, locale='RU', host='hh.ru'):
    url = f'https://api.hh.ru/employers/{employer_id}/managers/{manager_id}/limits/resume'
    params = {
        'locale': locale,
        'host': host
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            logger.warning(f"Доступ запрещен для менеджера (ID: {manager_id})")
            return "Нет данных или доступ запрещен."
        elif response.status_code == 404:
            logger.warning(f"Данных нет для менеджера (ID: {manager_id})")
            return "Нет данных или доступ запрещен."
        else:
            logger.error(f'Ошибка при получении лимитов для менеджера (ID: {manager_id}): {response.status_code}')
            return None
    except requests.Timeout:
        logger.error(f"Timeout при получении лимитов для менеджера (ID: {manager_id})")
        return None
    except requests.RequestException as e:
        logger.error(f"Ошибка сети при получении лимитов: {str(e)}")
        return None

# Страница с лимитами
@app.route('/limits')
def limits():
    try:
        access_token = get_valid_access_token()
    except Exception as e:
        flash(f"Ошибка: {str(e)}", "danger")
        return redirect(url_for('index'))

    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': USER_AGENT,
        'Accept': 'application/json'
    }

    # Получение информации о текущем пользователе
    user_info_url = 'https://api.hh.ru/me'
    try:
        user_response = requests.get(user_info_url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.Timeout:
        logger.error("Timeout при получении информации о пользователе")
        flash("Превышено время ожидания ответа от HH.ru. Попробуйте позже.", "danger")
        return redirect(url_for('index'))
    except requests.RequestException as e:
        logger.error(f"Ошибка сети при получении информации о пользователе: {str(e)}")
        flash("Ошибка соединения с HH.ru. Попробуйте позже.", "danger")
        return redirect(url_for('index'))
    if user_response.status_code != 200:
        flash(f"Ошибка при получении информации о пользователе: {user_response.status_code}\n{user_response.text}", "danger")
        return redirect(url_for('index'))

    user_info = user_response.json()
    employer = user_info.get('employer')
    if not employer or 'id' not in employer:
        flash("Не удалось получить employer_id из данных пользователя.", "danger")
        return redirect(url_for('index'))

    employer_id = employer['id']

    # Получение информации о текущем менеджере
    current_manager = user_info.get('manager')
    if not current_manager or 'id' not in current_manager:
        flash("Не удалось получить manager_id из данных пользователя.", "danger")
        return redirect(url_for('index'))

    manager_id = current_manager['id']

    # Получение информации о менеджере для полного имени
    manager_info = get_manager_info(employer_id, manager_id, headers)
    if manager_info:
        manager_name = manager_info.get('full_name', 'Без имени')
    else:
        manager_name = 'Без имени'

    # Получение лимитов просмотра резюме для менеджера
    limits = get_resume_view_limits(employer_id, manager_id, headers)
    if limits and isinstance(limits, dict):
        manager_limits = [{
            'manager_id': manager_id,
            'manager_name': manager_name,
            'limits': limits
        }]
    else:
        manager_limits = [{
            'manager_id': manager_id,
            'manager_name': manager_name,
            'limits': 'Нет данных или доступ запрещен.'
        }]
        # Дополнительный вывод ошибки в лог и флеш-сообщение
        flash(f"Не удалось получить лимиты для менеджера: {manager_name} (ID: {manager_id}). Возможные причины: отсутствуют назначенные лимиты или недостаточные права доступа.", "warning")

    return render_template('limits.html', managers=manager_limits)

# Страница выхода
@app.route('/logout')
def logout():
    session.clear()
    flash("Вы успешно вышли из системы.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '6859')))
