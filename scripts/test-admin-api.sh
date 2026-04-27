#!/bin/bash
# API test script for admin panel

API_URL="${1:-http://localhost:8000}"
ADMIN_PASSWORD="${2:-admin123}"

echo "=== Testing Admin Panel APIs ==="
echo ""

# Login
echo "1. Testing Admin Login..."
LOGIN=$(curl -s -X POST "$API_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$ADMIN_PASSWORD\"}")

TOKEN=$(echo $LOGIN | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  echo $LOGIN
  exit 1
fi

echo "✓ Login successful"
echo "Token: ${TOKEN:0:20}..."
echo ""

# Get Dashboard
echo "2. Testing Dashboard Endpoint..."
DASHBOARD=$(curl -s -X GET "$API_URL/api/admin/dashboard" \
  -H "Authorization: Bearer $TOKEN")

echo $DASHBOARD | jq '.'
echo ""

# List Tenants
echo "3. Testing List Tenants..."
TENANTS=$(curl -s -X GET "$API_URL/api/admin/tenants?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo $TENANTS | jq '.'
echo ""

echo "=== All tests completed ==="
