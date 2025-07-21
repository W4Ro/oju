#!/bin/bash
# Oju Project Installation Script

set -e

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

generate_password() { openssl rand -base64 18 | tr -d "=+/" | cut -c1-16; }
generate_secret_key() { openssl rand -base64 32; }

create_env_file() {
    read -p "Enter the domain name for your application (e.g., example.com): " domain_name
    read -p "Enter your email address for Let's Encrypt: " email
    postgres_password=$(generate_password)
    redis_password=$(generate_password)
    secret_key=$(generate_secret_key)

    cat > .env << EOF
# General settings
DOMAIN_NAME=$domain_name
API_URL=https://$domain_name/api
FRONTEND_URL=https://$domain_name

# Django settings
DEBUG=False
SECRET_KEY=$secret_key
DJANGO_ALLOWED_HOSTS=$domain_name,www.$domain_name
CORS_ALLOWED_ORIGINS=https://$domain_name,https://www.$domain_name

# Database settings
POSTGRES_DB=Oju_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$postgres_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis settings
REDIS_PASSWORD=$redis_password
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://:$redis_password@redis:6379/0

# Celery settings
CELERY_BROKER_URL=redis://:$redis_password@redis:6379/0
CELERY_RESULT_BACKEND=redis://:$redis_password@redis:6379/0

# Let's Encrypt settings
CERTBOT_EMAIL=$email

# Frontend settings
NODE_ENV=production
EOF

    success "Environment file created successfully."
    info "Environment variables:"
    echo
    echo "DOMAIN_NAME=$domain_name"
    echo "API_URL=https://$domain_name/api"
    echo "DJANGO_ALLOWED_HOSTS=$domain_name,www.$domain_name"
    echo "POSTGRES_DB=Oju_db"
    echo "POSTGRES_USER=postgres"
    echo "POSTGRES_PASSWORD=$postgres_password"
    echo "REDIS_PASSWORD=$redis_password"
    echo "SECRET_KEY=$secret_key"
    echo
}

# Check prerequisites
info "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { error "Docker is not installed. Please install Docker first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { error "Docker Compose is not installed. Please install Docker Compose first."; exit 1; }
command -v openssl >/dev/null 2>&1 || { error "OpenSSL is not installed. Please install OpenSSL first."; exit 1; }
success "All prerequisites are met."

# Check docker-compose.yml
info "Checking docker-compose.yml presence..."
[ ! -f docker-compose.yml ] && error "docker-compose.yml not found. Aborting." && exit 1
success "docker-compose.yml found."

# Configure .env file
info "Configuring environment file..."
if [ -f .env ]; then
    warning "The .env file already exists."
    read -p "Do you want to replace it? (y/N): " replace_env
    [[ $replace_env =~ ^[yY]$ ]] && create_env_file || info "Using existing .env file."
else
    create_env_file
fi

# Check for port conflicts
info "Checking if ports 80 and 443 are available..."
if lsof -i :80 || lsof -i :443; then
    warning "Ports 80 or 443 are already in use."
    read -p "Continue anyway? (y/N): " proceed
    [[ ! $proceed =~ ^[yY]$ ]] && error "Aborting installation." && exit 1
else
    success "Ports are available."
fi

# Build Docker images
info "Building Docker images..."

# Ensure Docker volumes are set correctly in docker-compose.yml
info "Checking volumes in docker-compose.yml..."
# This step is typically handled automatically by Docker Compose
info "Volumes checked and updated if necessary."

# Build the images with Docker Compose
docker-compose build
info "Docker images built successfully."

# Configure SSL certificates
info "Configuring SSL certificates..."

# Ask about Let's Encrypt staging mode
read -p "Do you want to use Let's Encrypt staging mode (for testing without rate limits)? (y/N): " use_staging
staging_flag=""
if [[ $use_staging == "y" || $use_staging == "Y" ]]; then
    staging_flag="--staging"
fi

# Collect SSL certificate info for self-signed fallback
read -p "Enter Country Name (2 letter code) [XX]: " ssl_country
ssl_country=${ssl_country:-XX}

read -p "Enter State or Province Name [State]: " ssl_state
ssl_state=${ssl_state:-State}

read -p "Enter City [City]: " ssl_city
ssl_city=${ssl_city:-City}

read -p "Enter Organization Name [Organization]: " ssl_org
ssl_org=${ssl_org:-Organization}

read -p "Enter Organizational Unit Name [IT]: " ssl_org_unit
ssl_org_unit=${ssl_org_unit:-IT}

# Export SSL certificate info as environment variables
echo "# SSL Certificate Info" >> .env
echo "SSL_COUNTRY=$ssl_country" >> .env
echo "SSL_STATE=$ssl_state" >> .env
echo "SSL_CITY=$ssl_city" >> .env
echo "SSL_ORG=$ssl_org" >> .env
echo "SSL_ORG_UNIT=$ssl_org_unit" >> .env

# Start Nginx first to handle ACME challenge
echo "### Starting Nginx ###"
docker-compose up -d nginx

# Request Let's Encrypt certificate
echo "### Requesting Let's Encrypt certificate for $domain_name ###"
CERTBOT_ARGS="--email $email -d $domain_name -d www.$domain_name --no-eff-email $staging_flag"

if ! docker-compose run --rm certbot-init $CERTBOT_ARGS; then
    warning "Failed to obtain Let's Encrypt certificate. Self-signed certificates will be used."
    USE_LETSENCRYPT=false
else
    success "Let's Encrypt certificates obtained successfully!"
    USE_LETSENCRYPT=true
fi

# Reload Nginx to use the new certificate
docker-compose exec nginx nginx -s reload

echo "### SSL setup completed! ###"
if [ "$USE_LETSENCRYPT" = true ]; then
    if [[ $use_staging == "y" || $use_staging == "Y" ]]; then
        warning "You used Let's Encrypt staging mode. The certificates are not trusted."
        warning "When you're ready for production, run: ./update-certs.sh"
    else
        success "Let's Encrypt certificates are successfully installed."
        info "Certificates will automatically renew every 60 days."
    fi
else
    warning "Using self-signed certificates. These are not trusted by browsers."
    info "You can try to get Let's Encrypt certificates later by running: ./update-certs.sh"
fi

# Start services
info "Starting services..."
docker-compose up -d postgres redis
info "Waiting for PostgreSQL to start..."
sleep 10

# Check PostgreSQL readiness
docker-compose exec postgres pg_isready -U postgres
echo

# Start remaining services
docker-compose up -d
info "All services have been started."

info "Waiting for backend to be ready..."
sleep 3

# Verify services
info "Verifying all services are running..."

# Function to check if a service is running
check_service() {
    local service=$1
    local container_id=$(docker-compose ps -q $service)
    
    if [ -z "$container_id" ]; then
        warning "Service $service container not found."
        return 1
    fi
    
    local status=$(docker inspect --format='{{.State.Running}}' $container_id 2>/dev/null)
    
    if [ "$status" != "true" ]; then
        warning "Service $service does not appear to be running. Please check: docker-compose logs $service"
        return 1
    fi
    
    return 0
}

# Check each service
check_service backend
check_service frontend
check_service nginx
check_service postgres
check_service redis
check_service celery_worker
check_service celery_beat
# check_service certbot

export PYTHONIOENCODING=utf-8

# Create Django superuser with retry logic
info "Creating a Django superuser..."

user_created=false
max_attempts=5
attempt=1

while [ "$user_created" = false ] && [ $attempt -le $max_attempts ]; do
    if [ $attempt -gt 1 ]; then
        warning "Attempt $attempt of $max_attempts to create superuser..."
    fi
    
    while true; do
        read -p "Enter superuser username (at least 3 alphabetic characters): " admin_username
        if [[ ! $admin_username =~ ^[a-zA-Z0-9]{3,}$ ]]; then
            warning "Username must be at least 3 alphabetic characters. Please try again."
        else
            break
        fi
    done

    while true; do
        read -p "Enter superuser email: " admin_email
        if [[ ! $admin_email =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
            warning "Please enter a valid email address."
        else
            break
        fi
    done

    # Check if user already exists
    exists_result=$(docker-compose exec backend python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('EXISTS') if User.objects.filter(username='$admin_username').exists() else print('NOT_EXISTS')")

    if [[ $exists_result == "EXISTS" ]]; then
        warning "A superuser with username '$admin_username' already exists."
        user_created=true
        break
    fi

    # Try to create superuser
    if docker-compose exec backend python3 manage.py createsuperuser --username $admin_username --email $admin_email; then
        # Verify superuser was created successfully
        verify_result=$(docker-compose exec backend python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.filter(username='$admin_username').first(); print('SUCCESS') if user and user.is_superuser else print('FAILED')")
        
        if [[ $verify_result == *"SUCCESS"* ]]; then
            success "Superuser '$admin_username' created and verified successfully."
            user_created=true
        else
            error "Superuser creation appeared to succeed but verification failed."
            ((attempt++))
        fi
    else
        error "Superuser creation failed."
        ((attempt++))
    fi
    
    if [ "$user_created" = false ] && [ $attempt -le $max_attempts ]; then
        warning "Retrying superuser creation..."
        sleep 2
    fi
done

if [ "$user_created" = false ]; then
    error "Failed to create superuser after $max_attempts attempts. Installation aborted."
    exit 1
fi

# Clean up Docker
read -p "Do you want to clean up unused Docker resources? (y/N): " cleanup
if [[ $cleanup =~ ^[yY]$ ]]; then
    info "Cleaning up unused Docker data..."
    docker system prune -f
    success "Docker cleanup completed."
fi


# Print success message
cat << EOF

================================================================
$(success "Installation completed successfully!")

You can access your application at:
https://$domain_name

To access the Django admin interface:
https://$domain_name/admin
================================================================
EOF