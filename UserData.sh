#!/bin/bash
set -e

GIT_REPO_URL="https://github.com/shabeebtk/turf-booking-management-django-rest-framework-backend.git"

PROJECT_MAIN_DIR_NAME="turf-booking-management-django-rest-framework-backend"

# Clone repository
git clone "$GIT_REPO_URL" "/home/ubuntu/$PROJECT_MAIN_DIR_NAME"

cd "/home/ubuntu/$PROJECT_MAIN_DIR_NAME"

# Make all .sh files executable
chmod +x scripts/*.sh

# Execute scripts for OS dependencies, Python dependencies, Gunicorn, Nginx, and starting the application
./scripts/instance_os_dependencies.sh
./scripts/python_dependencies.sh
./scripts/gunicorn.sh
./scripts/nginx.sh
./scripts/start_app.sh