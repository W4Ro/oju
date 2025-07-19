#!/bin/bash
# Backend entrypoint.sh - Only initializes on first container start
# Check if this is the first run by looking for a marker file
INIT_MARKER="/app/data/.initialized"

# wait for PostgreSQL and Redis to be ready before starting the Django application
echo "Waiting for PostgreSQL..."
timeout=60
start_time=$(date +%s)
until pg_isready -h postgres -U postgres -q || [ $(( $(date +%s) - start_time )) -ge $timeout ]; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

if pg_isready -h postgres -U postgres -q; then
  echo "PostgreSQL is ready!"
else
  echo "PostgreSQL connection timed out, but continuing anyway..."
fi

# wait for Redis to be ready
echo "Waiting for Redis..."
timeout=60
start_time=$(date +%s)
until redis-cli -h redis -a $REDIS_PASSWORD PING 2>/dev/null || [ $(( $(date +%s) - start_time )) -ge $timeout ]; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done

if redis-cli -h redis -a $REDIS_PASSWORD PING 2>/dev/null; then
  echo "Redis is ready!"
  
  # Flush Redis cache on every startup
  echo "Flushing Redis cache..."
  redis-cli -h redis -a $REDIS_PASSWORD FLUSHALL
  echo "Redis cache flushed!"
else
  echo "Redis connection timed out, but continuing anyway..."
fi

# Create needed directories if they don't exist
mkdir -p /app/data /app/logs /app/static

# If this is the first run, perform initialization
if [ ! -f "$INIT_MARKER" ]; then
    echo "First time container startup detected. Running initialization..."
    
    # Exécuter les migrations
    python3 manage.py makemigrations users
    python3 manage.py makemigrations roles
    python3 manage.py makemigrations AV_vendor
    python3 manage.py makemigrations cerb_scans
    python3 manage.py makemigrations config
    python3 manage.py makemigrations defacement
    python3 manage.py makemigrations entities
    python3 manage.py makemigrations focal_points
    python3 manage.py makemigrations logsFonc
    python3 manage.py makemigrations mail_setting
    python3 manage.py makemigrations alertes
    python3 manage.py makemigrations tools_integrated
    
    echo "Applying migrations..."

    python3 manage.py migrate
    
    # Run initialization commands
    echo "Running initialization commands..."
    python3 manage.py init_mailconfig
    python3 manage.py init_permissions
    python3 manage.py init_tools
    python3 manage.py init_config
    python3 manage.py initsubscan
    python3 manage.py init_focal_function
    python3 manage.py init_vendors
    
    # Create marker file to indicate initialization has been performed
    touch "$INIT_MARKER"
    echo "Initialization completed and marked."
else
    echo "Container has been initialized before. Skipping initialization steps."
    echo "Applying any new migrations..."
    python3 manage.py makemigrations
    python3 manage.py migrate
fi

# Collect static files (safe to run every time)
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Start Django application
echo "Starting Django application..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 core.wsgi:application