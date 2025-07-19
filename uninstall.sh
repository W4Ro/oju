#!/bin/bash
# Oju Project Uninstall Script

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

warning "This script will completely remove Oju Project containers, images, and volumes."
warning "All data will be lost. This action cannot be undone."
read -p "Are you sure you want to continue? (y/N): " confirm

if [[ $confirm != "y" && $confirm != "Y" ]]; then
    info "Uninstall canceled."
    exit 0
fi

info "Stopping all containers..."
docker-compose down

# Ask if volumes should be removed
read -p "Do you want to remove all volumes (database, media, etc.)? (y/N): " remove_volumes

if [[ $remove_volumes == "y" || $remove_volumes == "Y" ]]; then
    info "Removing all containers, networks, and volumes..."
    docker-compose down -v
    success "All containers, networks, and volumes have been removed."
else
    info "Removing containers and networks, keeping volumes..."
    docker-compose down
    success "All containers and networks have been removed. Volumes are preserved."
fi

# Ask if images should be removed
read -p "Do you want to remove all Docker images built for this project? (y/N): " remove_images

if [[ $remove_images == "y" || $remove_images == "Y" ]]; then
    info "Removing Docker images..."
    
    # Find and remove the images
    images=$(docker images | grep "Oju-" | awk '{print $3}')
    if [ -n "$images" ]; then
        echo $images | xargs docker rmi -f
        success "All project Docker images have been removed."
    else
        info "No project Docker images found."
    fi
else
    info "Docker images preserved."
fi

# Ask if the .env file should be removed
read -p "Do you want to remove the .env file? (y/N): " remove_env

if [[ $remove_env == "y" || $remove_env == "Y" ]]; then
    info "Removing .env file..."
    rm -f .env
    rm -f ./backend/data/.initialized
    success ".env file has been removed."
else
    info ".env file preserved."
fi

# Ask if SSL certificates should be removed
read -p "Do you want to remove SSL certificates (self-signed and Let's Encrypt)? (y/N): " remove_certs

if [[ $remove_certs == "y" || $remove_certs == "Y" ]]; then
    info "Removing SSL certificates..."
    rm -rf ./nginx/ssl
    docker volume rm Oju_certbot_data 2>/dev/null || true
    success "SSL certificates have been removed."
else
    info "SSL certificates preserved."
fi

success "Oju Project has been uninstalled successfully."