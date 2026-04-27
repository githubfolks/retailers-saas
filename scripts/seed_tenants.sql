-- Seed data for 5 initial tenants
INSERT INTO tenants (tenant_id, business_name, whatsapp_number, odoo_url, odoo_db, odoo_user, odoo_password, razorpay_key, razorpay_secret, n8n_webhook_url)
VALUES 
('acme-corp', 'Acme Global Solutions', '919876543210', 'https://acme.odoo.com', 'acme_prod', 'admin@acme.com', 'pass123', 'rzp_test_acme123', 'secret_acme_456', 'https://n8n.acme.com/webhook'),
('tech-flow', 'TechFlow Innovations', '919876543211', 'https://techflow.odoo.com', 'techflow_db', 'ops@techflow.io', 'secure_pass', 'rzp_test_tech789', 'secret_tech_012', 'https://n8n.techflow.io/webhook'),
('green-retail', 'GreenLeaf Retailers', '919876543212', 'https://greenleaf.odoo.com', 'green_prod', 'admin@greenleaf.com', 'green123', 'rzp_test_green345', 'secret_green_678', NULL),
('swift-logistics', 'Swift Logistics Group', '919876543213', 'https://swift.odoo.com', 'swift_db', 'super@swift.com', 'swift_secure', 'rzp_test_swift901', 'secret_swift_234', 'https://n8n.swift.com/webhook'),
('urban-style', 'UrbanStyle Fashion', '919876543214', 'https://urban.odoo.com', 'urban_style_db', 'manager@urban.style', 'style_pass', 'rzp_test_urban567', 'secret_urban_890', NULL);
