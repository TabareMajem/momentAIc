module.exports = {
    apps: [
        {
            name: "momentaic-backend",
            cwd: "/opt/momentaic/momentaic-backend",
            script: "gunicorn",
            args: "app.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 120",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "512M",
            env: {
                NODE_ENV: "production",
            }
        },
        {
            name: "momentaic-frontend",
            cwd: "/opt/momentaic/momentaic-frontend",
            script: "npm",
            args: "run preview -- --port 4173 --host",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "256M",
        }
    ]
};
