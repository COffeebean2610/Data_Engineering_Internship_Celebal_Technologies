USE sales_assignment;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'sales_assignment'
ORDER BY table_name;

SELECT * FROM customers ORDER BY id LIMIT 5;
SELECT * FROM products ORDER BY id LIMIT 5;
SELECT * FROM orders ORDER BY id LIMIT 5;
SELECT * FROM order_items ORDER BY id LIMIT 5;

SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items;
