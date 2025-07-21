# Oju Project Recovery Script for Windows

param([switch]$Help)

if ($Help) {
    Write-Host "Oju Project Recovery Script for Windows" -ForegroundColor Green
    Write-Host "Usage: .\recovery.ps1 [-Help]" -ForegroundColor Yellow
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

# Check prerequisites
info "Checking installation status..."
try {
    docker-compose ps | Out-Null
} catch {
    error "docker-compose configuration not found or docker not running."
    exit 1
}

# Check existing containers
info "Checking existing containers..."
try {
    $running_containers = (docker-compose ps --services --filter "status=running" | Measure-Object).Count
    
    if ($running_containers -eq 0) {
        warning "No running containers found. Starting fresh installation."
        if (Test-Path ".\install.ps1") {
            .\install.ps1
        } else {
            error "install.ps1 not found."
            exit 1
        }
        exit 0
    }
} catch {
    error "Failed to check container status."
    exit 1
}

# Give options for recovery
Write-Host "The following recovery options are available:"
Write-Host "1. Reset containers (keeps volumes/data)"
Write-Host "2. Reset everything (including volumes/data)"
Write-Host "3. Try to restart services"
Write-Host "4. Rebuild specific service"
Write-Host "5. Exit"

$option = Read-Host "Select option (1-5)"

switch ($option) {
    "1" {
        info "Resetting containers but keeping data..."
        try {
            docker-compose down
            docker-compose up -d
            success "Containers reset successfully."
        } catch {
            error "Failed to reset containers."
            exit 1
        }
    }
    
    "2" {
        info "Resetting everything including data..."
        $confirm = Read-Host "Are you SURE you want to delete ALL data? This cannot be undone. (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            try {
                docker-compose down -v
                if (Test-Path ".\install.ps1") {
                    .\install.ps1
                } else {
                    error "install.ps1 not found."
                    exit 1
                }
                success "Complete reset performed successfully."
            } catch {
                error "Failed to perform complete reset."
                exit 1
            }
        } else {
            info "Reset cancelled."
        }
    }
    
    "3" {
        info "Restarting services..."
        try {
            docker-compose restart
            success "Services restarted."
        } catch {
            error "Failed to restart services."
            exit 1
        }
    }
    
    "4" {
        $service = Read-Host "Enter service name (backend, frontend, nginx, postgres, redis, celery_worker, celery_beat)"
        info "Rebuilding $service..."
        try {
            docker-compose build $service
            docker-compose up -d $service
            success "$service rebuilt and restarted."
        } catch {
            error "Failed to rebuild $service."
            exit 1
        }
    }
    
    "5" {
        info "Exiting without changes."
        exit 0
    }
    
    default {
        error "Invalid option."
        exit 1
    }
}

# Check service status
info "Checking service status..."
try {
    docker-compose ps
} catch {
    warning "Could not check service status."
}

info "Recovery process complete."

# Get domain name from .env file
try {
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        $domainName = ($envContent | Where-Object { $_ -match "^DOMAIN_NAME=" }) -replace "DOMAIN_NAME=", ""
        if (![string]::IsNullOrEmpty($domainName)) {
            Write-Host "You can access your application at: https://$domainName"
        }
    }
} catch {
    # Ignore errors if .env file can't be read
}