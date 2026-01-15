#!/bin/bash
cd /opt/momentaic/momentaic-frontend

# Install dependencies if node_modules missing
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Run build
npm run build

# Start preview
exec npm run preview -- --port 4173 --host
