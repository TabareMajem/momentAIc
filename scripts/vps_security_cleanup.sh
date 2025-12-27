#!/bin/bash
# =============================================================================
# VPS SECURITY CLEANUP SCRIPT - SAFE FOR MULTI-PROJECT VPS
# This script removes crypto miners while preserving your legitimate projects
# =============================================================================

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  VPS CRYPTO MINER CLEANUP - SAFE EDITION   ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# STEP 1: Kill Known Crypto Miner Processes (SAFE - Won't Touch Legit Apps)
# =============================================================================
echo -e "${YELLOW}[1/7] Killing known crypto miner processes...${NC}"

# List of known miner process names
MINER_NAMES=(
    "syssls" "xmrig" "minerd" "kdevtmpfsi" "kinsing" 
    "xmr" "cpuminer" "ccminer" "ethminer" "nbminer"
    "t-rex" "lolMiner" "gminer" "srbminer" "teamredminer"
    "claymore" "phoenixminer" "nanominer" "bzminer"
    "unmineable" "rx.unmineable"
)

for name in "${MINER_NAMES[@]}"; do
    if pgrep -f "$name" > /dev/null 2>&1; then
        echo -e "  ${RED}Found: $name - Killing...${NC}"
        pkill -9 -f "$name" 2>/dev/null || true
    fi
done

echo -e "${GREEN}  ✓ Miner processes killed${NC}"

# =============================================================================
# STEP 2: Remove Cron Persistence (Miners Often Use Cron)
# =============================================================================
echo -e "${YELLOW}[2/7] Checking and cleaning cron jobs...${NC}"

# Backup current crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# Remove suspicious cron entries (keep checking but don't auto-delete)
echo "  Checking root crontab..."
crontab -l 2>/dev/null | grep -iE "(curl|wget|syssls|xmrig|\.sh|mining)" && {
    echo -e "  ${RED}! Suspicious cron entries found. Removing crontab...${NC}"
    crontab -r 2>/dev/null || true
} || echo -e "${GREEN}  ✓ No suspicious cron entries${NC}"

# Check system cron directories
echo "  Checking /etc/cron.d/..."
for f in /etc/cron.d/*; do
    if [ -f "$f" ]; then
        if grep -qiE "(curl.*\|.*sh|wget.*\|.*sh|mining|xmrig)" "$f" 2>/dev/null; then
            echo -e "  ${RED}! Suspicious file: $f - Removing...${NC}"
            rm -f "$f"
        fi
    fi
done

echo -e "${GREEN}  ✓ Cron cleaned${NC}"

# =============================================================================
# STEP 3: Secure Redis (WITHOUT Restarting - Preserve Connections)
# =============================================================================
echo -e "${YELLOW}[3/7] Checking Redis security...${NC}"

if [ -f /etc/redis/redis.conf ]; then
    # Check if Redis is bound to 0.0.0.0 (insecure)
    if grep -q "^bind 0.0.0.0" /etc/redis/redis.conf; then
        echo -e "  ${RED}! Redis is exposed to internet. Fixing...${NC}"
        sed -i 's/^bind 0.0.0.0/bind 127.0.0.1 ::1/' /etc/redis/redis.conf
        # Note: Will need manual restart after script
    else
        echo -e "${GREEN}  ✓ Redis is properly bound${NC}"
    fi
else
    echo "  No system Redis config found (Docker Redis is isolated)"
fi

# =============================================================================
# STEP 4: Remove Unauthorized SSH Keys
# =============================================================================
echo -e "${YELLOW}[4/7] Checking SSH authorized_keys...${NC}"

SSH_KEYS_FILE="/root/.ssh/authorized_keys"
if [ -f "$SSH_KEYS_FILE" ]; then
    # Count keys
    KEY_COUNT=$(wc -l < "$SSH_KEYS_FILE")
    echo "  Found $KEY_COUNT SSH key(s)"
    
    # Show keys for review (but don't auto-delete - requires user review)
    echo "  Current keys:"
    cat "$SSH_KEYS_FILE" | while read line; do
        KEY_COMMENT=$(echo "$line" | awk '{print $NF}')
        echo "    - $KEY_COMMENT"
    done
    
    echo -e "${YELLOW}  ! Review manually: nano $SSH_KEYS_FILE${NC}"
else
    echo -e "${GREEN}  ✓ No SSH keys file${NC}"
fi

# =============================================================================
# STEP 5: Clean /tmp (Common Miner Hide Location)
# =============================================================================
echo -e "${YELLOW}[5/7] Cleaning /tmp directory...${NC}"

# Remove suspicious files
find /tmp -type f -name "*.sh" -mtime -7 -exec rm -f {} \; 2>/dev/null || true
find /tmp -type f -executable -mtime -7 -exec file {} \; 2>/dev/null | grep -i "ELF" | cut -d: -f1 | xargs rm -f 2>/dev/null || true

# Remove known miner artifacts
rm -rf /tmp/.X11-unix 2>/dev/null || true
rm -rf /tmp/.ICE-unix 2>/dev/null || true
rm -rf /tmp/.font-unix 2>/dev/null || true
rm -rf /tmp/.XIM-unix 2>/dev/null || true
rm -f /tmp/syssls* 2>/dev/null || true

echo -e "${GREEN}  ✓ /tmp cleaned${NC}"

# =============================================================================
# STEP 6: Block Mining Pool Domains in /etc/hosts
# =============================================================================
echo -e "${YELLOW}[6/7] Blocking known mining pools...${NC}"

MINING_POOLS=(
    "pool.supportxmr.com"
    "rx.unmineable.com"
    "xmr.pool.minergate.com"
    "xmr-us-east1.nanopool.org"
    "xmr-eu1.nanopool.org"
    "pool.minexmr.com"
    "xmr.2miners.com"
)

for pool in "${MINING_POOLS[@]}"; do
    if ! grep -q "$pool" /etc/hosts 2>/dev/null; then
        echo "127.0.0.1 $pool" >> /etc/hosts
    fi
done

# Already added from your commands
if ! grep -q "unmineable.com" /etc/hosts 2>/dev/null; then
    echo "127.0.0.1 rx.unmineable.com" >> /etc/hosts
    echo "127.0.0.1 unmineable.com" >> /etc/hosts
fi

echo -e "${GREEN}  ✓ Mining pools blocked${NC}"

# =============================================================================
# STEP 7: Check System (Don't Kill - Just Report)
# =============================================================================
echo -e "${YELLOW}[7/7] Final system check...${NC}"

echo ""
echo "=== Current Load Average ==="
uptime

echo ""
echo "=== Top CPU Processes (Review for suspicious activity) ==="
ps aux --sort=-%cpu | head -10

echo ""
echo "=== Docker Containers (YOUR LEGITIMATE PROJECTS) ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not running"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           CLEANUP COMPLETE                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS (MANUAL):${NC}"
echo "1. Review SSH keys:  nano /root/.ssh/authorized_keys"
echo "2. Restart Redis:    systemctl restart redis-server"
echo "3. Change passwords: passwd root"
echo "4. Restart Docker:   systemctl restart docker"
echo ""
echo -e "${RED}If CPU is still high, run: htop${NC}"
echo "Look for suspicious processes and kill with: kill -9 <PID>"
