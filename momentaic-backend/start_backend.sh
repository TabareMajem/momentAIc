#!/bin/bash

# Ensure we are in the right directory
cd /opt/momentaic/momentaic-backend

# Copy .env from parent if needed
# Patch local .env if it exists (placed by deploy script)
if [ -f ".env" ]; then
    echo "Found local .env, patching hostnames for Docker-to-Host bridge..."
    # Database at 172.19.0.5, Redis at 172.19.0.4
    sed -i 's/@db/@172.19.0.5/g' .env
    sed -i 's/@postgres/@172.19.0.5/g' .env
    sed -i 's/@redis/@172.19.0.4/g' .env
    sed -i 's/:\/\/postgres/:\/\/172.19.0.5/g' .env
    sed -i 's/:\/\/db/:\/\/172.19.0.5/g' .env
    sed -i 's/:\/\/redis/:\/\/172.19.0.4/g' .env
    echo "✅ .env patching complete (DB: 172.19.0.5, Redis: 172.19.0.4)."
else
    echo "⚠️ No .env found in $(pwd), skipping patch."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || echo "Venv creation failed, falling back to system python"
fi

# Activate virtual environment if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Using system python"
fi

# Upgrade pip (ignore error)
pip install --upgrade pip --break-system-packages || true

# Install dependencies
echo "Installing/Updating dependencies..."
pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt

# Start Gunicorn
echo "Starting Gunicorn..."
exec python3 -m gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 120
