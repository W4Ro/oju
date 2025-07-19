-#!/bin/bash
# Oju Project Recovery Script

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

# Check prerequisites
info "Checking installation status..."
if ! docker-compose ps >/dev/null 2>&1; then
    error "docker-compose configuration not found or docker not running."
    exit 1
fi

# Check existing containers
info "Checking existing containers..."
running_containers=$(docker-compose ps --services --filter "status=running" | wc -l)
if [ "$running_containers" -eq "0" ]; then
    warning "No running containers found. Starting fresh installation."
    ./install.sh
    exit 0
fi

# Give options for recovery
echo "The following recovery options are available:"
echo "1. Reset containers (keeps volumes/data)"
echo "2. Reset everything (including volumes/data)"
echo "3. Try to restart services"
echo "4. Rebuild specific service"
echo "5. Exit"

read -p "Select option (1-5): " option

case $option in
    1)
        info "Resetting containers but keeping data..."
        docker-compose down
        docker-compose up -d
        success "Containers reset successfully."
        ;;
    2)
        info "Resetting everything including data..."
        read -p "Are you SURE you want to delete ALL data? This cannot be undone. (y/N): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            docker-compose down -v
            ./install.sh
            success "Complete reset performed successfully."
        else
            info "Reset cancelled."
        fi
        ;;
    3)
        info "Restarting services..."
        docker-compose restart
        success "Services restarted."
        ;;
    4)
        read -p "Enter service name (backend, frontend, nginx, postgres, redis, celery_worker, celery_beat): " service
        info "Rebuilding $service..."
        docker-compose build $service
        docker-compose up -d $service
        success "$service rebuilt and restarted."
        ;;
    5)
        info "Exiting without changes."
        exit 0
        ;;
    *)
        error "Invalid option."
        exit 1
        ;;
esac

# Check service status
info "Checking service status..."
docker-compose ps

info "Recovery process complete."
echo "You can access your application at: https://$(grep DOMAIN_NAME .env | cut -d= -f2)"