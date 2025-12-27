#!/bin/bash
set -e

echo "=== MOMENTAIC FRONTEND RECOVERY ==="

# 1. Navigate to frontend directory
cd "/opt/momentaic/momentaic front"

# 2. Install dependencies (in case of missing modules)
echo "[1/4] Installing dependencies..."
npm install

# 3. Build the project (Critical for 'vite preview')
echo "[2/4] Building production assets..."
npm run build

# 4. Reset PM2 configuration
echo "[3/4] Configuring PM2..."
pm2 stop momentaic-frontend || true
pm2 delete momentaic-frontend || true

# Write safe config
cat > /opt/momentaic/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: "momentaic-frontend",
      script: "npm",
      args: "run preview -- --port 2685",
      cwd: "/opt/momentaic/momentaic front",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      restart_delay: 5000,
      env: {
        PORT: 2685,
        NODE_ENV: "production",
      },
    },
  ],
};
EOF

# 5. Start
echo "[4/4] Starting Service..."
pm2 start /opt/momentaic/ecosystem.config.js
pm2 save

echo "=== ✅ RECOVERY COMPLETE ==="
pm2 list
