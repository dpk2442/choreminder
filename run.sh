#!/bin/bash
# Script that gets executed in Docker containers

# Activate virtual environment
source .venv/bin/activate

# Create data folder
mkdir -p data
chown -R www-data: data

# Run database migrations
python manage.py migrate

# Generate secret key file if needed
python manage.py generate_secret_key

# Download vendor libraries if needed
python manage.py download_vendor_libs

# Collect static files
python manage.py collectstatic

# Start uwsgi server
uwsgi uwsgi.ini
