# Используем легкий образ Python
FROM python:3.12-slim-bookworm

# Метаданные
LABEL maintainer="HH Limits Service"
LABEL description="Lightweight Flask application for viewing HeadHunter resume limits"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
# Делаем это отдельным слоем для кеширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app.py .
COPY gunicorn_config.py .
COPY templates/ templates/

# Создаем непривилегированного пользователя для безопасности
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт приложения
EXPOSE 6859

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1

# Healthcheck для мониторинга
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:6859/', timeout=2)" || exit 1

# Запускаем приложение через Gunicorn для production
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
