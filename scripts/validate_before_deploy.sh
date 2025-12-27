#!/bin/bash
# Pre-deployment validation script for MomentAIc
# Run this BEFORE any deployment to VPS

set -e

echo "=== MOMENTAIC PRE-DEPLOYMENT VALIDATION ==="
echo ""

cd /root/momentaic/momentaic-backend

# Step 1: Syntax Check
echo "[1/3] Running Python Syntax Check..."
python3 -m py_compile app/main.py app/core/config.py app/agents/*.py
echo "✅ Syntax check passed"

# Step 2: Import Test
echo ""
echo "[2/3] Running Import Test..."
python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test:test@localhost/test'
os.environ['SECRET_KEY'] = 'testtesttesttesttesttesttesttesttest'
os.environ['JWT_SECRET_KEY'] = 'testtesttesttesttesttesttesttesttest'
from app.agents.base import get_llm
print('✅ Import test passed')
"

# Step 3: Model Configuration Check
echo ""
echo "[3/3] Checking LLM Model Configuration..."
MODEL=$(grep -oP 'model="[^"]+"' app/agents/base.py | head -1)
echo "Current model: $MODEL"

if [[ "$MODEL" == *"gemini-2.5-pro"* ]]; then
    echo "✅ Model is set to gemini-2.5-pro (recommended)"
else
    echo "⚠️  WARNING: Model is NOT gemini-2.5-pro. Verify this is intentional."
fi

echo ""
echo "=== VALIDATION COMPLETE ==="
echo ""
echo "If all checks passed, you may proceed with deployment."
echo "Recommended deployment command:"
echo "  cd /opt/momentaic && git pull && pm2 restart all"
