FROM nginx:1.23-alpine

RUN apk update && \
    apk add --no-cache openssl curl ca-certificates && \
    rm -rf /var/cache/apk/*

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/app.conf.template /etc/nginx/conf.d/app.conf.template

RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=XX/ST=State/L=City/O=Organization/CN=localhost" \
    -addext "subjectAltName=DNS:localhost"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /var/www/certbot

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]