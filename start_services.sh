#!/bin/bash

# Start the FastAPI backend in the background
gunicorn neoserve_ai.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &

# Start Nginx in the foreground
exec nginx -g 'daemon off;'
