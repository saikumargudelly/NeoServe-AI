#!/bin/bash
set -e

# Build the React frontend
echo "Building React frontend..."
cd /app/neoserve-ai-frontend
npm install
npm run build

# Copy built frontend to Nginx directory
echo "Copying frontend files to Nginx directory..."
cp -r build/* /var/www/html/

# Set permissions
echo "Setting permissions..."
chmod -R 755 /var/www/html

# Start the FastAPI backend in the background
echo "Starting FastAPI backend..."
cd /app
gunicorn neoserve_ai.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &

# Start Nginx in the foreground
echo "Starting Nginx..."
exec nginx -g 'daemon off;'
