import os
import subprocess
import time

VPS_HOST = "207.180.227.179"
VPS_USER = "root"
VPS_PASS = "Cruyff14-88888888"
VPS_DIR = "/opt/momentaic/momentaic-backend"

FILES_TO_UPLOAD = {
    "/root/momentaic/momentaic-backend/docker-compose.yml": f"{VPS_DIR}/docker-compose.yml",
    "/root/momentaic/momentaic-backend/app/core/config.py": f"{VPS_DIR}/app/core/config.py",
    "/root/momentaic/safe_activate.sh": "/root/safe_activate.sh",
}

def run_ssh_cmd(cmd):
    full_cmd = f"sshpass -p '{VPS_PASS}' ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} \"{cmd}\""
    print(f"Running: {cmd}")
    ret = os.system(full_cmd)
    if ret != 0:
        print(f"Error running command: {cmd}")
        return False
    return True

def upload_file(local_path, remote_path):
    print(f"Uploading {local_path} -> {remote_path}")
    cmd = f"sshpass -p '{VPS_PASS}' scp -o StrictHostKeyChecking=no {local_path} {VPS_USER}@{VPS_HOST}:{remote_path}"
    ret = os.system(cmd)
    if ret != 0:
        print(f"Failed to upload {local_path}")
        return False
    return True

def main():
    print("🚀 Starting Automated Fix Deployment...")
    
    # 1. Upload Files
    for local, remote in FILES_TO_UPLOAD.items():
        if not upload_file(local, remote):
            print("❌ Upload failed. Aborting.")
            return

    # 2. Fix Nginx
    print("🔧 Fixing Nginx Conflict...")
    run_ssh_cmd("bash /root/safe_activate.sh")

    # 3. Restart Backend with Limits
    print("🔄 Restarting Backend with Low CPU Limits...")
    restart_cmds = [
        f"cd {VPS_DIR}",
        "docker-compose down api", # clean stop
        "docker-compose up -d --no-deps --build api", # rebuild with new config
        "docker system prune -f" # Cleanup to save space
    ]
    
    combined_cmd = " && ".join(restart_cmds)
    run_ssh_cmd(combined_cmd)
    
    print("✅ Deployment Complete. Verifying...")
    time.sleep(5)
    os.system("curl -I https://momentaic.com/api/v1/health")

if __name__ == "__main__":
    main()
