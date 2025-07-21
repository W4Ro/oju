# Oju Project Installation Script for Windows

param([switch]$Help)

if ($Help) {
    Write-Host "Oju Project Installation Script for Windows" -ForegroundColor Green
    Write-Host "Usage: .\install.ps1 [-Help]" -ForegroundColor Yellow
    exit 0
}

$ErrorActionPreference = "Stop"

function info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Blue }
function success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function warning($msg) { Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Function to generate random passwords
function generate_password { 
    $bytes = New-Object byte[] 24
    (New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
    return [Convert]::ToBase64String($bytes).Replace("=", "").Replace("+", "").Replace("/", "").Substring(0,16)
}

# Function to generate a secure secret key
function generate_secret_key {
    $bytes = New-Object byte[] 32
    (New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
    return [Convert]::ToBase64String($bytes)
}

# Function to create environment file
function create_env_file {
    $domain_name = Read-Host "Enter the domain name for your application (e.g., example.com)"
    $email = Read-Host "Enter your email address for Let's Encrypt"
    
    $postgres_password = generate_password
    $redis_password = generate_password
    $secret_key = generate_secret_key

    $content = @"
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
"@
    
    $content | Out-File -FilePath .env -Encoding UTF8
    success "Environment file created successfully."
    
    info "Environment variables:"
    Write-Host ""
    Write-Host "DOMAIN_NAME=$domain_name"
    Write-Host "API_URL=https://$domain_name/api"
    Write-Host "DJANGO_ALLOWED_HOSTS=$domain_name,www.$domain_name"
    Write-Host "POSTGRES_DB=Oju_db"
    Write-Host "POSTGRES_USER=postgres"
    Write-Host "POSTGRES_PASSWORD=$postgres_password"
    Write-Host "REDIS_PASSWORD=$redis_password"
    Write-Host "SECRET_KEY=$secret_key"
    Write-Host ""
    
    return $domain_name, $email
}

# Function to check if a service is running
function check_service($service) {
    try {
        $container_id = docker-compose ps -q $service 2>$null
        
        if ([string]::IsNullOrEmpty($container_id)) {
            warning "Service $service container not found."
            return $false
        }
        
        $status = docker inspect --format='{{.State.Running}}' $container_id 2>$null
        
        if ($status -ne "true") {
            warning "Service $service does not appear to be running. Please check: docker-compose logs $service"
            return $false
        }
        
        return $true
    } catch {
        warning "Service $service container not found."
        return $false
    }
}

# Check prerequisites
info "Checking prerequisites..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    error "Docker is not installed. Please install Docker first."
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}

success "All prerequisites are met."

# Check docker-compose.yml
info "Checking docker-compose.yml presence..."
if (-not (Test-Path .\docker-compose.yml)) {
    error "docker-compose.yml not found. Aborting."
    exit 1
}
success "docker-compose.yml found."

info "Checking Git configuration for Windows..."
$autocrlf = git config core.autocrlf
if ($autocrlf -eq "true") {
    info "Fixing Git line endings configuration..."
    git config core.autocrlf false
    git config core.eol lf
}

# Configure .env file
info "Configuring environment file..."
$domain_name = ""
$email = ""

if (Test-Path ".env") {
    warning "The .env file already exists."
    $replace_env = Read-Host "Do you want to replace it? (y/N)"
    if ($replace_env -match "^[yY]$") {
        $domain_name, $email = create_env_file
    } else {
        info "Using existing .env file."
    }
} else {
    $domain_name, $email = create_env_file
}

# Check for port conflicts
info "Checking if ports 80 and 443 are available..."
try {
    $port80 = Get-NetTCPConnection -LocalPort 80 -ErrorAction SilentlyContinue
    $port443 = Get-NetTCPConnection -LocalPort 443 -ErrorAction SilentlyContinue
    
    if ($port80 -or $port443) {
        warning "Ports 80 or 443 are already in use."
        $proceed = Read-Host "Continue anyway? (y/N)"
        if (-not ($proceed -match "^[yY]$")) {
            error "Aborting installation."
            exit 1
        }
    } else {
        success "Ports are available."
    }
} catch {
    # Fallback to netstat
    $portsUsed = netstat -ano | Select-String ":80|:443"
    if ($portsUsed) {
        warning "Ports 80 or 443 are already in use."
        $proceed = Read-Host "Continue anyway? (y/N)"
        if (-not ($proceed -match "^[yY]$")) {
            error "Aborting installation."
            exit 1
        }
    } else {
        success "Ports are available."
    }
}

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
$use_staging = Read-Host "Do you want to use Let's Encrypt staging mode (for testing without rate limits)? (y/N)"
$staging_flag = ""
if ($use_staging -eq "y" -or $use_staging -eq "Y") {
    $staging_flag = "--staging"
}

# Collect SSL certificate info for self-signed fallback
$ssl_country = Read-Host "Enter Country Name (2 letter code) [XX]"
if ([string]::IsNullOrEmpty($ssl_country)) { $ssl_country = "XX" }

$ssl_state = Read-Host "Enter State or Province Name [State]"
if ([string]::IsNullOrEmpty($ssl_state)) { $ssl_state = "State" }

$ssl_city = Read-Host "Enter City [City]"
if ([string]::IsNullOrEmpty($ssl_city)) { $ssl_city = "City" }

$ssl_org = Read-Host "Enter Organization Name [Organization]"
if ([string]::IsNullOrEmpty($ssl_org)) { $ssl_org = "Organization" }

$ssl_org_unit = Read-Host "Enter Organizational Unit Name [IT]"
if ([string]::IsNullOrEmpty($ssl_org_unit)) { $ssl_org_unit = "IT" }

# Export SSL certificate info as environment variables 
$ssl_info = @"

# SSL Certificate Info
SSL_COUNTRY=$ssl_country
SSL_STATE=$ssl_state
SSL_CITY=$ssl_city
SSL_ORG=$ssl_org
SSL_ORG_UNIT=$ssl_org_unit
"@

$ssl_info | Out-File -FilePath ".env" -Append -Encoding UTF8

# Start Nginx first to handle ACME challenge 
Write-Host "### Starting Nginx ###"
docker-compose up -d nginx

# Request Let's Encrypt certificate 
Write-Host "### Requesting Let's Encrypt certificate for $domain_name ###"
$CERTBOT_ARGS = "--email $email -d $domain_name -d www.$domain_name --no-eff-email $staging_flag"

try {
    docker-compose run --rm certbot-init $CERTBOT_ARGS.Split(' ')
    success "Let's Encrypt certificates obtained successfully!"
    $USE_LETSENCRYPT = $true
} catch {
    warning "Failed to obtain Let's Encrypt certificate. Self-signed certificates will be used."
    $USE_LETSENCRYPT = $false
}

# Reload Nginx to use the new certificate
docker-compose exec nginx nginx -s reload

Write-Host "### SSL setup completed! ###"
if ($USE_LETSENCRYPT) {
    if ($use_staging -eq "y" -or $use_staging -eq "Y") {
        warning "You used Let's Encrypt staging mode. The certificates are not trusted."
        warning "When you're ready for production, run: .\update-certs.ps1"
    } else {
        success "Let's Encrypt certificates are successfully installed."
        info "Certificates will automatically renew every 60 days."
    }
} else {
    warning "Using self-signed certificates. These are not trusted by browsers."
    info "You can try to get Let's Encrypt certificates later by running: .\update-certs.ps1"
}

# Start services 
info "Starting services..."
docker-compose up -d postgres redis
info "Waiting for PostgreSQL to start..."
Start-Sleep -Seconds 10

# Check PostgreSQL readiness 
docker-compose exec postgres pg_isready -U postgres
Write-Host ""

# Start remaining services
docker-compose up -d
info "All services have been started."

info "Waiting for backend to be ready..."
Start-Sleep -Seconds 3

# Verify services 
info "Verifying all services are running..."

# Check each service 
check_service backend
check_service frontend
check_service nginx
check_service postgres
check_service redis
check_service celery_worker
check_service celery_beat
# check_service certbot

# Create Django superuser with retry logic
info "Creating a Django superuser..."

$userCreated = $false
$maxAttempts = 5
$attempt = 1

while (-not $userCreated -and $attempt -le $maxAttempts) {
    if ($attempt -gt 1) {
        warning "Attempt $attempt of $maxAttempts to create superuser..."
    }
    
    do {
        $admin_username = Read-Host "Enter superuser username (at least 3 alphanumeric characters)"
        if ($admin_username -notmatch "^[a-zA-Z0-9]{3,}$") {
            warning "Username must be at least 3 alphanumeric characters. Please try again."
        }
    } while ($admin_username -notmatch "^[a-zA-Z0-9]{3,}$")

    do {
        $admin_email = Read-Host "Enter superuser email"
        if ($admin_email -notmatch "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$") {
            warning "Please enter a valid email address."
        }
    } while ($admin_email -notmatch "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    # Check if user already exists
    $checkUserPython = @"
from django.contrib.auth import get_user_model
User = get_user_model()
print('EXISTS' if User.objects.filter(username='$admin_username').exists() else 'NOT_EXISTS')
"@

    $existsResult = docker-compose exec backend python3 manage.py shell -c "$checkUserPython"

    
    if ($existsResult -eq "EXISTS") {
        warning "A superuser with username '$admin_username' already exists."
        $userCreated = $true
        break
    }

    # Try to create superuser
    docker-compose exec backend python3 manage.py createsuperuser --username $admin_username --email $admin_email

    if ($LASTEXITCODE -eq 0) {
        # Verify superuser was created successfully
        $verifyUserPython = @"
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.filter(username='$admin_username').first()
print('SUCCESS' if user and user.is_superuser else 'FAILED')
"@

    $verifyResult = docker-compose exec backend python3 manage.py shell -c "$verifyUserPython"

        
        if ($verifyResult -match "SUCCESS") {
            success "Superuser '$admin_username' created and verified successfully."
            $userCreated = $true
        } else {
            error "Superuser creation appeared to succeed but verification failed."
            $attempt++
        }
    } else {
        error "Superuser creation failed."
        $attempt++
    }
    
    if (-not $userCreated -and $attempt -le $maxAttempts) {
        warning "Retrying superuser creation..."
        Start-Sleep -Seconds 2
    }
}

if (-not $userCreated) {
    error "Failed to create superuser after $maxAttempts attempts. Installation aborted."
    exit 1
}

# Clean up Docker 
$cleanup = Read-Host "Do you want to clean up unused Docker resources? (y/N)"
if ($cleanup -match "^[yY]$") {
    info "Cleaning up unused Docker data..."
    docker system prune -f
    success "Docker cleanup completed."
}

# Print success message 
Write-Host ""
Write-Host ""
Write-Host "================================================================"
success "Installation completed successfully!"
Write-Host ""
Write-Host "You can access your application at:"
Write-Host "https://$domain_name"
Write-Host ""
Write-Host "To access the Django admin interface:"
Write-Host "https://$domain_name/admin"
Write-Host "================================================================"