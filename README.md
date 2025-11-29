# HH Limits - Сервис просмотра лимитов резюме на HeadHunter

## Описание

HH Limits - веб-приложение на Flask, которое позволяет просматривать информацию о лимитах просмотра резюме для менеджеров через API HeadHunter. Сервис использует OAuth 2.0 для авторизации и получения данных из API HH.ru.

## Быстрый старт с Docker (рекомендуется)

### Предварительные требования

- Docker 20.10+
- Docker Compose 2.0+

### Запуск в Docker

1. Клонируйте репозиторий и перейдите в директорию:
```bash
cd hh_limits
```

2. Создайте файл `.env` из шаблона:
```bash
cp .env.example .env
```

3. Отредактируйте `.env` файл и заполните обязательные параметры:
```bash
nano .env
```

Обязательно заполните:
- `CLIENT_ID` - ID приложения из https://dev.hh.ru/admin
- `CLIENT_SECRET` - секретный ключ приложения
- `REDIRECT_URI` - URL обратного вызова (например, https://yourdomain.com/callback)
- `SECRET_KEY` - сгенерируйте криптографически стойкий ключ:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

4. Запустите приложение:
```bash
docker-compose up -d
```

5. Приложение будет доступно по адресу: `http://localhost:6859`

### Управление контейнером

Просмотр логов:
```bash
docker-compose logs -f
```

Остановка приложения:
```bash
docker-compose down
```

Перезапуск:
```bash
docker-compose restart
```

Пересборка после изменений:
```bash
docker-compose up -d --build
```

Проверка статуса:
```bash
docker-compose ps
```

### Размер образа

Образ оптимизирован для минимального размера:
- Базовый образ: `python:3.12-slim-bookworm`
- Размер: ~150-200 MB
- Только необходимые зависимости
- Непривилегированный пользователь для безопасности

### Запуск без Docker Compose

Если вы хотите использовать только Docker:

```bash
# Сборка образа
docker build -t hh-limits:latest .

# Запуск контейнера
docker run -d \
  --name hh_limits_app \
  -p 6859:6859 \
  --env-file .env \
  --restart unless-stopped \
  hh-limits:latest
```

Управление:
```bash
# Просмотр логов
docker logs -f hh_limits_app

# Остановка
docker stop hh_limits_app

# Запуск
docker start hh_limits_app

# Удаление
docker rm -f hh_limits_app
```

## Настройка

### Зависимости

Для работы сервиса требуются следующие библиотеки Python:
- Flask
- requests
- python-dotenv

Установка зависимостей:
```bash
pip install flask requests python-dotenv
```

### Файл конфигурации .env

Настройки сервиса хранятся в файле `.env` в корневой директории проекта. Пример содержимого файла:

```
CLIENT_ID=ВАШ_CLIENT_ID
CLIENT_SECRET=ВАШ_CLIENT_SECRET
REDIRECT_URI=https://your-domain.com/callback
SECRET_KEY=your_flask_secret_key
ACCESS_TOKEN=
REFRESH_TOKEN=
ACCESS_TOKEN_EXPIRES_AT=
PORT=6859
```

Обязательные параметры:
- `CLIENT_ID` - ID приложения из личного кабинета разработчика HH.ru
- `CLIENT_SECRET` - секретный ключ приложения из личного кабинета разработчика HH.ru
- `REDIRECT_URI` - URL обратного вызова, который должен совпадать с URL, указанным при регистрации приложения
- `SECRET_KEY` - секретный ключ для Flask-сессий
- `PORT` - порт, на котором будет запущен сервис (по умолчанию 6859)

Параметры, которые заполняются автоматически после первой авторизации:
- `ACCESS_TOKEN` - токен доступа к API HH.ru
- `REFRESH_TOKEN` - токен обновления
- `ACCESS_TOKEN_EXPIRES_AT` - дата и время истечения токена доступа

### Получение учетных данных для API HH.ru

1. Зарегистрируйте приложение на странице [https://dev.hh.ru/admin](https://dev.hh.ru/admin)
2. Укажите REDIRECT_URI (например, https://your-domain.com/callback)
3. Получите CLIENT_ID и CLIENT_SECRET и добавьте их в файл `.env`

## Запуск сервиса

### Запуск вручную

Для запуска сервиса выполните:

```bash
python app.py
```

Сервис будет доступен по адресу `http://0.0.0.0:6859`.

### Запуск через systemd (для Linux)

Для автоматического запуска сервиса при старте системы, создайте файл конфигурации systemd:

```bash
sudo nano /etc/systemd/system/hh_limits.service
```

Содержимое файла:

```ini
[Unit]
Description=HH Limits Service
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/hh_limits
ExecStart=/usr/bin/python3 /path/to/hh_limits/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Замените `your_username` и `/path/to/hh_limits` на ваши значения.

Активация и запуск сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hh_limits
sudo systemctl start hh_limits
```

## Остановка сервиса

### Остановка запущенного вручную приложения

Нажмите Ctrl+C в терминале, где запущено приложение.

### Остановка сервиса через systemd

```bash
sudo systemctl stop hh_limits
```

## Перезапуск сервиса

### Перезапуск вручную

Остановите сервис (Ctrl+C) и запустите снова:

```bash
python app.py
```

### Перезапуск через systemd

```bash
sudo systemctl restart hh_limits
```

## Проверка статуса

Для проверки статуса сервиса через systemd:

```bash
sudo systemctl status hh_limits
```

## Просмотр логов

Для просмотра логов сервиса через systemd:

```bash
sudo journalctl -u hh_limits
```

С опцией -f для отслеживания логов в реальном времени:

```bash
sudo journalctl -f -u hh_limits
```

## Использование

1. Откройте в браузере `http://your-domain:6859`
2. Нажмите на кнопку "Войти через HH.ru"
3. Пройдите авторизацию на HH.ru
4. После успешной авторизации вы будете перенаправлены на страницу с лимитами просмотра резюме

## Файлы проекта

- `app.py` - основной файл приложения Flask
- `get.py` - вспомогательный скрипт для работы с токенами вне веб-интерфейса
- `templates/` - директория с HTML-шаблонами
  - `index.html` - стартовая страница
  - `limits.html` - страница с лимитами просмотра резюме
  - `home.html` - альтернативная главная страница
- `.env` - файл с настройками

## Дополнительно

Для обновления токена вне веб-интерфейса можно использовать скрипт `get.py`:

```bash
python get.py
```

Скрипт сохранит результаты в файл с именем вида `manager_limits_YYYYMMDD_HHMMSS.txt`.

## Безопасность

### Важные рекомендации:

1. **Никогда не коммитьте `.env` файл в git**
   - Используйте `.env.example` как шаблон
   - Файл `.env` уже добавлен в `.gitignore`

2. **Генерируйте криптографически стойкий SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Используйте HTTPS в production**
   - Настройте reverse proxy (nginx, Caddy)
   - Используйте SSL-сертификаты (Let's Encrypt)

4. **Регулярно обновляйте зависимости**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

5. **Контейнер запускается от непривилегированного пользователя**
   - Повышает безопасность
   - Ограничивает потенциальный ущерб при компрометации

### Известные ограничения:

- `get.py` модифицирует `.env` файл - не используйте в Docker контейнере
- Сессии хранятся на диске - в production рекомендуется использовать Redis
- User-Agent содержит email - вынесите в переменную окружения если нужно

## Лицензия

Проект создан для работы с API HeadHunter. Убедитесь, что соблюдаете условия использования API HH.ru.
