FROM nginx

# Удаляем старые конфигурации
RUN rm -f /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Копируем статические файлы
COPY client/static /app/static

# Копируем конфигурацию Nginx
COPY client/nginx.conf /etc/nginx/nginx.conf