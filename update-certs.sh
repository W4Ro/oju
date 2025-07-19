#!/bin/bash
# Oju Project Certificate Update Script

set -e

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored information messages
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to print success messages
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to print warnings
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to print errors
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
if [ ! -f .env ]; then
    error "No .env file found. Please run install.sh first."
    exit 1
fi
source .env

# Ask about staging mode
read -p "Do you want to use Let's Encrypt staging mode (for testing without rate limits)? (y/N): " use_staging
staging_flag=""
if [[ $use_staging == "y" || $use_staging == "Y" ]]; then
    staging_flag="--staging"
fi

# Ensure Nginx is running
info "Making sure Nginx is running..."
docker-compose up -d nginx

# Request new certificates
info "Requesting Let's Encrypt certificate for $DOMAIN_NAME..."
CERTBOT_ARGS="--email $CERTBOT_EMAIL -d $DOMAIN_NAME -d www.$DOMAIN_NAME --no-eff-email $staging_flag"

if ! docker-compose run --rm certbot-init $CERTBOT_ARGS; then
    error "Failed to obtain Let's Encrypt certificates. Please check your domain configuration."
    exit 1
fi

# Reload Nginx to use the new certificates
info "Reloading Nginx with new certificates..."
docker-compose exec nginx nginx -s reload

success "Certificate update completed successfully!"
if [[ $use_staging == "y" || $use_staging == "Y" ]]; then
    warning "You used Let's Encrypt staging mode. The certificates are not trusted."
    info "Run this script again without staging mode when ready for production."
else
    success "Let's Encrypt certificates are successfully installed and will be renewed automatically."
fi