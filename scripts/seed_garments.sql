-- Seed data for 'Thread & Trend' (Garment Business)
INSERT INTO tenants (tenant_id, business_name, whatsapp_number, odoo_url, odoo_db, odoo_user, odoo_password, razorpay_key, razorpay_secret, n8n_webhook_url)
VALUES 
('thread-trend', 'Thread & Trend Garments', '919888777666', 'https://garments.odoo.com', 'garment_prod', 'ops@threadtrend.com', 'garments123', 'rzp_test_garment999', 'secret_garment_888', 'https://n8n.hook.garments.com');

-- Garment Products
INSERT INTO products (tenant_id, name, description, price, sku, quantity)
VALUES 
('thread-trend', 'Classic Crewneck Tee (White)', '100% Organic Cotton, Soft-touch finish, True to size', 1200.0, 'TT-TSH-WHT-01', 250),
('thread-trend', 'Slim Fit Selvedge Denim', '14oz Raw Denim, Contrast stitching, Tapered leg', 4500.0, 'TT-DMN-BLU-02', 80),
('thread-trend', 'Linen Summer Dress (Emerald)', 'Breathable linen, Floral print, Adjustable waist', 3200.0, 'TT-DRS-EMR-03', 45),
('thread-trend', 'Leather Moto Jacket', 'Premium lambskin, Quilted lining, Silver hardware', 18500.0, 'TT-JKT-LTH-04', 12),
('thread-trend', 'Merino Wool Scarf (Grey)', 'Heavyweight merino, Ribbed texture, One size', 2800.0, 'TT-SCR-GRY-05', 120);

-- Garment Order History (Seasonal Spike)
INSERT INTO orders (tenant_id, customer_mobile, product_name, quantity, unit_price, total_amount, status, payment_status, created_at)
VALUES 
('thread-trend', '919000000010', 'Classic Crewneck Tee (White)', 2, 1200.0, 2400.0, 'completed', 'completed', NOW() - INTERVAL '1 day'),
('thread-trend', '919000000011', 'Leather Moto Jacket', 1, 18500.0, 18500.0, 'pending', 'pending', NOW() - INTERVAL '4 hours'),
('thread-trend', '919000000012', 'Slim Fit Selvedge Denim', 1, 4500.0, 4500.0, 'completed', 'completed', NOW() - INTERVAL '2 days'),
('thread-trend', '919000000013', 'Linen Summer Dress (Emerald)', 1, 3200.0, 3200.0, 'completed', 'completed', NOW() - INTERVAL '3 days'),
('thread-trend', '919000000014', 'Merino Wool Scarf (Grey)', 3, 2800.0, 8400.0, 'completed', 'completed', NOW() - INTERVAL '5 days');
