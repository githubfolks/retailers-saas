-- Seed data for products and orders for acme-corp
INSERT INTO products (tenant_id, name, description, price, sku, quantity)
VALUES 
('acme-corp', 'Premium Subscription', 'Access to all Acme premium features', 5000.0, 'ACME-PREM-01', 100),
('acme-corp', 'Professional Node', 'High-performance compute node', 12000.0, 'ACME-NODE-PRO', 15),
('acme-corp', 'Grid API Access', 'Enterprise API integration key', 25000.0, 'ACME-API-ENT', 50);

INSERT INTO orders (tenant_id, customer_mobile, product_name, quantity, unit_price, total_amount, status, payment_status, created_at)
VALUES 
('acme-corp', '919000000001', 'Premium Subscription', 1, 5000.0, 5000.0, 'completed', 'completed', NOW() - INTERVAL '1 day'),
('acme-corp', '919000000002', 'Professional Node', 2, 12000.0, 24000.0, 'pending', 'pending', NOW() - INTERVAL '2 hours'),
('acme-corp', '919000000003', 'Grid API Access', 1, 25000.0, 25000.0, 'completed', 'completed', NOW() - INTERVAL '1 week');
