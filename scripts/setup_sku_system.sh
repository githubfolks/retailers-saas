#!/bin/bash
# SKU System Setup Script
# Run this to get your SKU system up and running

set -e

echo "========================================"
echo "SKU SYSTEM SETUP"
echo "========================================"
echo ""

# Check PostgreSQL
echo "1️⃣  Checking PostgreSQL..."
if docker ps | grep -q postgres; then
    echo "   ✓ PostgreSQL is running"
else
    echo "   ℹ️  Starting PostgreSQL..."
    docker-compose up -d postgres
    sleep 5
fi

echo ""
echo "2️⃣  Activating virtual environment..."
cd /Users/vikram/workspace/odoo-saas
source venv/bin/activate
echo "   ✓ Virtual environment activated"

echo ""
echo "3️⃣  Running SKU migration..."
python3 scripts/migrate_sku_system.py
echo ""

echo "========================================"
echo "✅ SKU SYSTEM READY"
echo "========================================"
echo ""
echo "📋 Next, run the server:"
echo "   python3 app/main.py"
echo ""
echo "📚 Then access the API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔍 Try these endpoints:"
echo "   GET /sku/lookup/SHIRT-BLUE-001"
echo "   GET /sku/lookup/barcode/1234567890001"
echo "   GET /sku/search?q=shirt"
echo "   GET /sku/low-stock/list"
echo ""
