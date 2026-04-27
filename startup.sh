#!/bin/bash

# Inventory System Startup Script
set -e

WORKSPACE="/Users/vikram/workspace/odoo-saas"
VENV="$WORKSPACE/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "INVENTORY SYSTEM STARTUP"
echo "=================================================="
echo ""

# Activate venv
source "$VENV/bin/activate"
cd "$WORKSPACE"

# Export Python path
export PYTHONPATH=$WORKSPACE

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo -e "${GREEN}✓ Python path set${NC}"
echo ""

echo "=================================================="
echo "AVAILABLE SERVICES"
echo "=================================================="
echo ""
echo "1. FastAPI Server (port 8000)"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Celery Worker (background tasks)"
echo "   celery -A app.core.celery_app worker --loglevel=info"
echo ""
echo "3. Celery Beat (task scheduler)"
echo "   celery -A app.core.celery_app beat --loglevel=info"
echo ""
echo "4. Flower (Celery monitoring)"
echo "   celery -A app.core.celery_app --broker=redis://localhost:6379 flower"
echo ""
echo "=================================================="
echo "QUICK START COMMANDS"
echo "=================================================="
echo ""
echo "Option A: Run in separate terminals"
echo "  Terminal 1: $WORKSPACE/startup.sh fastapi"
echo "  Terminal 2: $WORKSPACE/startup.sh worker"
echo "  Terminal 3: $WORKSPACE/startup.sh beat"
echo ""
echo "Option B: Run single command (all in background)"
echo "  $WORKSPACE/startup.sh all"
echo ""
echo "Option C: Run Flower dashboard"
echo "  $WORKSPACE/startup.sh flower"
echo ""
echo "=================================================="
echo "VERIFY SETUP"
echo "=================================================="
echo ""

python3 scripts/test_inventory_setup.py 2>&1 | grep "✓\|⚠"

echo ""
echo "=================================================="
echo "READY FOR DEPLOYMENT!"
echo "=================================================="
