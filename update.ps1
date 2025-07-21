# Oju Project Update Script for Windows

param([switch]$Help)

if ($Help) {
    Write-Host "Oju Project Update Script for Windows" -ForegroundColor Green
    Write-Host "Usage: .\update.ps1 [-Help]" -ForegroundColor Yellow
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

# Check if .env file exists
if (!(Test-Path ".env")) {
    error "Environment file .env not found. Please run install.ps1 first."
    exit 1
}

# Check what to update
Write-Host "What would you like to update?"
Write-Host "1. Full update (rebuild all containers and update code)"
Write-Host "2. Update code only (no container rebuild)"
Write-Host "3. Update SSL certificates"
Write-Host "4. Apply database migrations"
Write-Host "5. Collect static files"

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        info "Performing full update..."
        
        # Pull latest code if it's a git repository
        if (Test-Path ".git") {
            info "Pulling latest code from git repository..."
            try {
                git pull
            } catch {
                warning "Git pull failed. Continuing with container rebuild..."
            }
        } else {
            warning "Not a git repository. Skipping code update."
        }
        
        # Rebuild and restart containers
        info "Rebuilding and restarting containers..."
        try {
            docker-compose down
            docker-compose build
            docker-compose up -d
        } catch {
            error "Failed to rebuild containers."
            exit 1
        }
        
        # Apply migrations
        info "Applying database migrations..."
        try {
            docker-compose exec backend python3 manage.py makemigrations
            docker-compose exec backend python3 manage.py migrate
        } catch {
            warning "Database migrations failed."
        }
        
        # Collect static files
        info "Collecting static files..."
        try {
            docker-compose exec backend python3 manage.py collectstatic --noinput
        } catch {
            warning "Static files collection failed."
        }
        
        success "Full update completed successfully!"
    }
    
    "2" {
        info "Updating code only..."
        
        # Pull latest code if it's a git repository
        if (Test-Path ".git") {
            info "Pulling latest code from git repository..."
            try {
                git pull
            } catch {
                warning "Not a git repository. Skipping code update."
                exit 1
            }
        } else {
            warning "Not a git repository. Skipping code update."
            exit 1
        }
        
        # Restart containers without rebuilding
        info "Restarting containers..."
        try {
            docker-compose restart backend frontend
        } catch {
            error "Failed to restart containers."
            exit 1
        }
        
        success "Code update completed successfully!"
    }
    
    "3" {
        info "Updating SSL certificates..."
        
        # Get domain name from .env file
        try {
            $envContent = Get-Content ".env"
            $domain_name = ($envContent | Where-Object { $_ -match "^DOMAIN_NAME=" }) -replace "DOMAIN_NAME=", ""
            $email = ($envContent | Where-Object { $_ -match "^CERTBOT_EMAIL=" }) -replace "CERTBOT_EMAIL=", ""
            
            if ([string]::IsNullOrEmpty($domain_name) -or [string]::IsNullOrEmpty($email)) {
                error "Domain name or email not found in .env file."
                exit 1
            }
        } catch {
            error "Failed to read .env file."
            exit 1
        }
        
        # Ask about Let's Encrypt staging mode
        $use_staging = Read-Host "Do you want to use Let's Encrypt staging mode (for testing without rate limits)? (y/N)"
        $staging_flag = ""
        if ($use_staging -eq "y" -or $use_staging -eq "Y") {
            $staging_flag = "--staging"
        }
        
        # Request new certificate
        info "Requesting new Let's Encrypt certificate for $domain_name..."
        try {
            $certbotCmd = "docker-compose run --rm certbot certbot certonly --webroot -w /var/www/certbot --email $email -d $domain_name -d www.$domain_name --agree-tos --no-eff-email --force-renewal"
            if ($staging_flag -ne "") {
                $certbotCmd += " $staging_flag"
            }
            
            Invoke-Expression $certbotCmd
        } catch {
            error "Failed to request SSL certificate."
            exit 1
        }
        
        # Reload Nginx to use the new certificate
        info "Reloading Nginx to use the new certificate..."
        try {
            docker-compose exec nginx nginx -s reload
        } catch {
            error "Failed to reload Nginx."
            exit 1
        }
        
        success "SSL certificates updated successfully!"
    }
    
    "4" {
        info "Applying database migrations..."
        try {
            docker-compose exec backend python manage.py migrate
            success "Database migrations applied successfully!"
        } catch {
            error "Database migrations failed."
            exit 1
        }
    }
    
    "5" {
        info "Collecting static files..."
        try {
            docker-compose exec backend python manage.py collectstatic --noinput
            success "Static files collected successfully!"
        } catch {
            error "Static files collection failed."
            exit 1
        }
    }
    
    default {
        error "Invalid choice. Please enter a number between 1 and 5."
        exit 1
    }
}