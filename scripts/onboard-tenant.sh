#!/bin/bash
# Tenant Onboarding Script
# Creates a new tenant via admin API

API_URL="${1:-http://localhost:8000}"
ADMIN_PASSWORD="${2:-admin123}"

echo "=== Odoo SaaS Tenant Onboarding ==="
echo ""

# Step 1: Admin Login
echo "Step 1: Authenticating admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"$ADMIN_PASSWORD\"}")

ADMIN_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ADMIN_TOKEN" ]; then
  echo "❌ Admin authentication failed"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✓ Admin authenticated"
echo ""

# Step 2: Collect tenant information
echo "Step 2: Enter tenant information"
echo ""

read -p "Enter Tenant ID (unique identifier): " TENANT_ID
read -p "Enter Business Name: " BUSINESS_NAME
read -p "Enter WhatsApp Number (91xxxxxxxxxx): " WHATSAPP_NUMBER
read -p "Enter Odoo URL: " ODOO_URL
read -p "Enter Odoo Database: " ODOO_DB
read -p "Enter Odoo Username: " ODOO_USER
read -s -p "Enter Odoo Password: " ODOO_PASSWORD
echo ""
read -p "Enter Razorpay Key: " RAZORPAY_KEY
read -s -p "Enter Razorpay Secret: " RAZORPAY_SECRET
echo ""
read -p "Enter n8n Webhook URL (optional, press Enter to skip): " N8N_WEBHOOK

# Step 3: Create tenant
echo ""
echo "Step 3: Creating tenant..."

CREATE_RESPONSE=$(curl -s -X POST "$API_URL/api/admin/tenants" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{
    \"tenant_id\": \"$TENANT_ID\",
    \"business_name\": \"$BUSINESS_NAME\",
    \"whatsapp_number\": \"$WHATSAPP_NUMBER\",
    \"odoo_url\": \"$ODOO_URL\",
    \"odoo_db\": \"$ODOO_DB\",
    \"odoo_user\": \"$ODOO_USER\",
    \"odoo_password\": \"$ODOO_PASSWORD\",
    \"razorpay_key\": \"$RAZORPAY_KEY\",
    \"razorpay_secret\": \"$RAZORPAY_SECRET\",
    \"n8n_webhook_url\": \"$N8N_WEBHOOK\"
  }")

if echo $CREATE_RESPONSE | grep -q "tenant_id"; then
  echo "✓ Tenant created successfully"
  echo ""
  echo "Tenant Details:"
  echo $CREATE_RESPONSE | jq '.'
else
  echo "❌ Failed to create tenant"
  echo "Response: $CREATE_RESPONSE"
  exit 1
fi

echo ""
echo "=== Tenant Onboarding Complete ==="
echo ""
echo "Next steps:"
echo "1. Test WhatsApp integration"
echo "2. Verify Odoo connectivity"
echo "3. Configure Razorpay payment links"
echo "4. Set up n8n workflows"
