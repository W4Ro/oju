# Oju Project Uninstall Script for Windows

param([switch]$Help)

if ($Help) {
    Write-Host "Oju Project Uninstall Script for Windows" -ForegroundColor Green
    Write-Host "Usage: .\uninstall.ps1 [-Help]" -ForegroundColor Yellow
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

# Warning messages
warning "This script will completely remove Oju Project containers, images, and volumes."
warning "All data will be lost. This action cannot be undone."

$confirm = Read-Host "Are you sure you want to continue? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    info "Uninstall canceled."
    exit 0
}

# Stopping all containers
info "Stopping all containers..."
try {
    docker-compose down
} catch {
    # Continue even if docker-compose down fails
}

# Ask if volumes should be removed
$remove_volumes = Read-Host "Do you want to remove all volumes (database, media, etc.)? (y/N)"
if ($remove_volumes -eq "y" -or $remove_volumes -eq "Y") {
    info "Removing all containers, networks, and volumes..."
    try {
        docker-compose down -v
    } catch {
        # Continue even if it fails
    }
    success "All containers, networks, and volumes have been removed."
} else {
    info "Removing containers and networks, keeping volumes..."
    try {
        docker-compose down
    } catch {
        # Continue even if it fails
    }
    success "All containers and networks have been removed. Volumes are preserved."
}

# Ask if images should be removed
$remove_images = Read-Host "Do you want to remove all Docker images built for this project? (y/N)"
if ($remove_images -eq "y" -or $remove_images -eq "Y") {
    info "Removing Docker images..."
    
    # Find and remove the images
    try {
        $images = docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}" | Where-Object { $_ -match "Oju-" }
        
        if ($images) {
            $imageIds = $images | ForEach-Object { 
                $parts = $_ -split '\s+'
                if ($parts.Length -ge 3) { $parts[2] }
            } | Where-Object { $_ -and $_ -ne "ID" }
            
            if ($imageIds) {
                $imageIds | ForEach-Object { docker rmi -f $_ }
                success "All project Docker images have been removed."
            } else {
                info "No project Docker images found."
            }
        } else {
            info "No project Docker images found."
        }
    } catch {
        info "No project Docker images found."
    }
} else {
    info "Docker images preserved."
}

# Ask if the .env file should be removed
$remove_env = Read-Host "Do you want to remove the .env file? (y/N)"
if ($remove_env -eq "y" -or $remove_env -eq "Y") {
    info "Removing .env file..."
    
    # Remove .env file
    if (Test-Path ".env") {
        Remove-Item ".env" -Force
    }
    
    # Remove ./backend/data/.initialized
    if (Test-Path ".\backend\data\.initialized") {
        Remove-Item ".\backend\data\.initialized" -Force
    }
    
    success ".env file has been removed."
} else {
    info ".env file preserved."
}

# Ask if SSL certificates should be removed
$remove_certs = Read-Host "Do you want to remove SSL certificates (self-signed and Let's Encrypt)? (y/N)"
if ($remove_certs -eq "y" -or $remove_certs -eq "Y") {
    info "Removing SSL certificates..."
    
    # Remove ./nginx/ssl directory
    if (Test-Path ".\nginx\ssl") {
        Remove-Item ".\nginx\ssl" -Recurse -Force
    }
    
    # Remove docker volume
    try {
        docker volume rm Oju_certbot_data 2>$null
    } catch {
        # Ignore errors, just like bash with || true
    }
    
    success "SSL certificates have been removed."
} else {
    info "SSL certificates preserved."
}

# Final success message
success "Oju Project has been uninstalled successfully."