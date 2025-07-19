#!/bin/bash
# Oju Project Update Script

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

# Check if .env file exists
if [ ! -f .env ]; then
    error "Environment file .env not found. Please run install.sh first."
    exit 1
fi

# Check what to update
echo "What would you like to update?"
echo "1. Full update (rebuild all containers and update code)"
echo "2. Update code only (no container rebuild)"
echo "3. Update SSL certificates"
echo "4. Apply database migrations"
echo "5. Collect static files"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        info "Performing full update..."
        
        # Pull latest code if it's a git repository
        if [ -d .git ]; then
            info "Pulling latest code from git repository..."
            git pull
        else
            warning "Not a git repository. Skipping code update."
        fi
        
        # Rebuild and restart containers
        info "Rebuilding and restarting containers..."
        docker-compose down
        docker-compose build
        docker-compose up -d
        
        # Apply migrations
        info "Applying database migrations..."
        docker-compose exec backend python3 manage.py makemigrations
        docker-compose exec backend python3 manage.py migrate
        
        # Collect static files
        info "Collecting static files..."
        docker-compose exec backend python3 manage.py collectstatic --noinput
        
        success "Full update completed successfully!"
        ;;
        
    2)
        info "Updating code only..."
        
        # Pull latest code if it's a git repository
        if [ -d .git ]; then
            info "Pulling latest code from git repository..."
            git pull
        else
            warning "Not a git repository. Skipping code update."
            exit 1
        fi
        
        # Restart containers without rebuilding
        info "Restarting containers..."
        docker-compose restart backend frontend
        
        success "Code update completed successfully!"
        ;;
        
    3)
        info "Updating SSL certificates..."
        
        # Get domain name from .env file
        domain_name=$(grep DOMAIN_NAME .env | cut -d '=' -f2)
        email=$(grep CERTBOT_EMAIL .env | cut -d '=' -f2)
        
        if [ -z "$domain_name" ] || [ -z "$email" ]; then
            error "Domain name or email not found in .env file."
            exit 1
        fi
        
        # Ask about Let's Encrypt staging mode
        read -p "Do you want to use Let's Encrypt staging mode (for testing without rate limits)? (y/N): " use_staging
        staging_flag=""
        if [[ $use_staging == "y" || $use_staging == "Y" ]]; then
            staging_flag="--staging"
        fi
        
        # Request new certificate
        info "Requesting new Let's Encrypt certificate for $domain_name..."
        docker-compose run --rm certbot certbot certonly --webroot -w /var/www/certbot \
            --email $email \
            -d $domain_name -d www.$domain_name \
            --agree-tos --no-eff-email \
            --force-renewal \
            $staging_flag
        
        # Reload Nginx to use the new certificate
        info "Reloading Nginx to use the new certificate..."
        docker-compose exec nginx nginx -s reload
        
        success "SSL certificates updated successfully!"
        ;;
        
    4)
        info "Applying database migrations..."
        docker-compose exec backend python manage.py migrate
        success "Database migrations applied successfully!"
        ;;
        
    5)
        info "Collecting static files..."
        docker-compose exec backend python manage.py collectstatic --noinput
        success "Static files collected successfully!"
        ;;
        
    *)
        error "Invalid choice. Please enter a number between 1 and 5."
        exit 1
        ;;
esac