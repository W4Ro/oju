# Oju Project Certificate Update Script for Windows

param([switch]$Help)

if ($Help) {
    Write-Host "Oju Project Certificate Update Script for Windows" -ForegroundColor Green
    Write-Host "Usage: .\update-certs.ps1 [-Help]" -ForegroundColor Yellow
    exit 0
}

$ErrorActionPreference = "Stop"

# Function to print colored information messages
function info($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Blue
}

# Function to print success messages
function success($msg) {
    Write-Host "[SUCCESS] $msg" -ForegroundColor Green
}

# Function to print warnings
function warning($msg) {
    Write-Host "[WARNING] $msg" -ForegroundColor Yellow
}

# Function to print errors
function error($msg) {
    Write-Host "[ERROR] $msg" -ForegroundColor Red
}

# Load environment variables
if (!(Test-Path ".env")) {
    error "No .env file found. Please run install.ps1 first."
    exit 1
}

# Source .env file
try {
    $envContent = Get-Content ".env"
    foreach ($line in $envContent) {
        if ($line -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Variable -Name $name -Value $value -Scope Script
        }
    }
} catch {
    error "Failed to load environment variables from .env file."
    exit 1
}

# Check required variables
if ([string]::IsNullOrEmpty($DOMAIN_NAME) -or [string]::IsNullOrEmpty($CERTBOT_EMAIL)) {
    error "DOMAIN_NAME or CERTBOT_EMAIL not found in .env file."
    exit 1
}

# Ask about staging mode
$use_staging = Read-Host "Do you want to use Let's Encrypt staging mode (for testing without rate limits)? (y/N)"
$staging_flag = ""
if ($use_staging -eq "y" -or $use_staging -eq "Y") {
    $staging_flag = "--staging"
}

# Ensure Nginx is running
info "Making sure Nginx is running..."
try {
    docker-compose up -d nginx
} catch {
    error "Failed to start Nginx."
    exit 1
}

# Request new certificates
info "Requesting Let's Encrypt certificate for $DOMAIN_NAME..."
$CERTBOT_ARGS = "--email $CERTBOT_EMAIL -d $DOMAIN_NAME -d www.$DOMAIN_NAME --no-eff-email $staging_flag"

try {
    $certbotCmd = "docker-compose run --rm certbot-init $CERTBOT_ARGS"
    Invoke-Expression $certbotCmd
} catch {
    error "Failed to obtain Let's Encrypt certificates. Please check your domain configuration."
    exit 1
}

# Reload Nginx to use the new certificates
info "Reloading Nginx with new certificates..."
try {
    docker-compose exec nginx nginx -s reload
} catch {
    error "Failed to reload Nginx."
    exit 1
}

success "Certificate update completed successfully!"

# Final messages based on staging mode
if ($use_staging -eq "y" -or $use_staging -eq "Y") {
    warning "You used Let's Encrypt staging mode. The certificates are not trusted."
    info "Run this script again without staging mode when ready for production."
} else {
    success "Let's Encrypt certificates are successfully installed and will be renewed automatically."
}