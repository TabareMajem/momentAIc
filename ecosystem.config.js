module.exports = {
    apps: [
        {
            name: "momentaic-backend",
            cwd: "/root/momentaic/momentaic-backend",
            script: "./start_backend.sh",
            interpreter: "bash",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "512M",
            env: {
                NODE_ENV: "production",
                POSTGRES_SERVER: "127.0.0.1"
            }
        },
        {
            name: "momentaic-frontend",
            cwd: "/root/momentaic/momentaic-frontend",
            script: "./start_frontend.sh",
            interpreter: "bash",
            exec_mode: "fork",
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: "256M",
        }
    ]
};
