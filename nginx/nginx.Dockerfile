FROM nginx:latest

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/cert.key -out /etc/nginx/cert.crt -subj \
    "/C=FR/ST=Denial/L=Springfield/O=Dis/CN=api.example.com"

