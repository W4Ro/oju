#!/bin/sh
set -e

if [ -z "$DOMAIN_NAME" ]; then
    echo "DOMAIN_NAME not set, using localhost as default"
    export DOMAIN_NAME=localhost
fi

envsubst '$DOMAIN_NAME' < /etc/nginx/conf.d/app.conf.template > /etc/nginx/conf.d/app.conf

if [ ! -d "/etc/letsencrypt/live/$DOMAIN_NAME" ] || [ ! -f "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" ]; then
    echo "Let's Encrypt certificates not found. Using self-signed certificates for now."
    
    if [ ! -f "/etc/nginx/ssl/cert.pem" ] || [ ! -f "/etc/nginx/ssl/key.pem" ]; then
        echo "Self-signed certificates not found. Generating them..."
        mkdir -p /etc/nginx/ssl
        SSL_COUNTRY=${SSL_COUNTRY:-XX}
        SSL_STATE=${SSL_STATE:-State}
        SSL_CITY=${SSL_CITY:-City}
        SSL_ORG=${SSL_ORG:-Organization}
        SSL_ORG_UNIT=${SSL_ORG_UNIT:-IT}
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/key.pem \
            -out /etc/nginx/ssl/cert.pem \
            -subj "/C=$SSL_COUNTRY/ST=$SSL_STATE/L=$SSL_CITY/O=$SSL_ORG/OU=$SSL_ORG_UNIT/CN=$DOMAIN_NAME" \
            -addext "subjectAltName=DNS:$DOMAIN_NAME,DNS:www.$DOMAIN_NAME"
        
        echo "Self-signed certificates generated successfully."
    fi
    
    sed -i "s|ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;|ssl_certificate /etc/nginx/ssl/cert.pem;|g" /etc/nginx/conf.d/app.conf
    sed -i "s|ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;|ssl_certificate_key /etc/nginx/ssl/key.pem;|g" /etc/nginx/conf.d/app.conf
fi

echo "Waiting for backend service to be available..."
timeout=120
elapsed=0
while ! ping -c1 backend &>/dev/null; do
    if [ "$elapsed" -ge "$timeout" ]; then
        echo "Backend not available after $timeout seconds, continuing anyway..."
        break
    fi
    echo "Backend not yet available. Waiting..."
    sleep 5
    elapsed=$((elapsed + 5))
done

if [ "$elapsed" -lt "$timeout" ]; then
    echo "Backend is available. Starting Nginx..."
else
    echo "Starting Nginx without backend connection..."
fi

# Démarrer nginx
exec nginx -g 'daemon off;'