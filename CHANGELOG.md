# Changelog

## [2.0.0] - 2024-11-29

### Исправления безопасности

- Сгенерирован криптографически стойкий SECRET_KEY вместо дефолтного значения
- Удалены ACCESS_TOKEN и REFRESH_TOKEN из .env (токены теперь хранятся только в Flask session)
- Вынесен User-Agent в переменную окружения для защиты email
- Добавлены защитные флаги для cookie: HttpOnly и SameSite

### Улучшения производительности и надежности

- Добавлен timeout (10 секунд) ко всем HTTP запросам
- Добавлена обработка исключений requests.Timeout и requests.RequestException
- Заменен Flask dev server на Gunicorn для production
- Добавлен gunicorn_config.py с оптимальными настройками

### Улучшения качества кода

- Добавлено централизованное логирование в app.log
- Добавлена валидация кода авторизации (regex проверка)
- Заменены print() на logger.error/warning/info
- Улучшена обработка ошибок сети

### Docker улучшения

- Обновлен Dockerfile для использования Gunicorn
- Добавлен gunicorn_config.py в образ
- Размер образа: 141 MB (легкий)

### Изменения конфигурации

- Обновлен .env.example с новой переменной USER_AGENT
- Удалены токены из .env.example (токены хранятся в session)
- Обновлен .gitignore для app.log

### Новые файлы

- gunicorn_config.py - конфигурация WSGI сервера для production
- CHANGELOG.md - история изменений

### Breaking Changes

- Удалены ACCESS_TOKEN, REFRESH_TOKEN, ACCESS_TOKEN_EXPIRES_AT из .env
- В app.py токены теперь хранятся только в Flask session
- get.py больше не рекомендуется использовать в Docker (модифицирует .env)

### Что нужно сделать после обновления

1. Обновите .env файл:
   ```bash
   # Добавьте новую переменную
   USER_AGENT=HH Limits/1.0 (your_email@example.com)

   # Удалите старые токены (если есть)
   # ACCESS_TOKEN=...
   # REFRESH_TOKEN=...
   # ACCESS_TOKEN_EXPIRES_AT=...
   ```

2. Сгенерируйте новый SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Пересоберите Docker образ:
   ```bash
   docker-compose up -d --build
   ```

## [1.0.0] - 2024-12-06

### Начальная версия

- Базовая функциональность Flask приложения
- OAuth 2.0 авторизация через HH.ru API
- Просмотр лимитов резюме для менеджеров
- Docker контейнеризация
