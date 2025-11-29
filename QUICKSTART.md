# Быстрый запуск за 3 шага

## 1. Настройте .env

```bash
cp .env.example .env
nano .env
```

Заполните только эти 4 параметра:
```env
CLIENT_ID=ваш_id_с_hh.ru
CLIENT_SECRET=ваш_секрет_с_hh.ru
REDIRECT_URI=https://ваш-домен.com/callback
SECRET_KEY=результат_команды_ниже
```

Генерация SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 2. Запустите

```bash
docker-compose up -d
```

## 3. Готово!

Откройте: http://localhost:6859

---

## Управление

**Логи:**
```bash
docker-compose logs -f
```

**Остановить:**
```bash
docker-compose down
```

**Перезапустить:**
```bash
docker-compose restart
```

**Обновить после изменений:**
```bash
docker-compose up -d --build
```

---

## Получение CLIENT_ID и CLIENT_SECRET

1. Зайдите на https://dev.hh.ru/admin
2. Создайте приложение
3. В REDIRECT_URI укажите ваш домен + `/callback`
4. Скопируйте CLIENT_ID и CLIENT_SECRET

---

Вот и всё!
