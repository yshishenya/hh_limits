#!/bin/bash

echo "🚀 Запуск HH Limits..."
echo ""

# Проверка .env
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте его: cp .env.example .env"
    echo "И заполните: CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SECRET_KEY"
    exit 1
fi

# Проверка обязательных переменных
source .env
if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ Не все обязательные переменные заполнены в .env"
    echo "Нужны: CLIENT_ID, CLIENT_SECRET, SECRET_KEY, REDIRECT_URI"
    exit 1
fi

# Запуск
echo "✅ Настройки проверены"
echo "🐳 Запускаем Docker контейнер..."
docker compose up -d

echo ""
echo "✨ Готово!"
echo "📱 Откройте: http://localhost:6859"
echo ""
echo "Для просмотра логов: docker compose logs -f"
