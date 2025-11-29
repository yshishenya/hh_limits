# HH Limits

Просмотр лимитов резюме на HeadHunter

## Запуск за 3 команды

```bash
# 1. Настройка
cp .env.example .env
nano .env  # Заполните CLIENT_ID, CLIENT_SECRET, SECRET_KEY

# 2. Запуск
./start.sh

# 3. Готово!
# Откройте http://localhost:6859
```

## Управление

```bash
docker-compose logs -f      # Логи
docker-compose restart      # Перезапуск
docker-compose down         # Остановка
```

## Получение ключей

1. https://dev.hh.ru/admin
2. Создать приложение
3. Скопировать CLIENT_ID и CLIENT_SECRET

## Генерация SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

**Размер:** 141 MB  
**Порт:** 6859  
**Сервер:** Gunicorn (production ready)

Детали в [QUICKSTART.md](QUICKSTART.md)
