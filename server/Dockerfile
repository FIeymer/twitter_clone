# Используем базовый образ с Python
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev \
    supervisor \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /server

# Копируем код приложения
COPY /server /server

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /server/requirements.txt

# Запускаем Supervisor, чтобы управлять всеми процессами
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
