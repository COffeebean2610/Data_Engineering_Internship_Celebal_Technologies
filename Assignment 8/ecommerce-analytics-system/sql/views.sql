-- Reusable analytics layer. Views never duplicate source data and refresh at query time.
DROP VIEW IF EXISTS customer_summary;
CREATE VIEW customer_summary AS SELECT c.customer_id, c.customer_name, c.customer_type, COUNT(DISTINCT o.order_id) AS order_count, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS lifetime_value FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name, c.customer_type;

DROP VIEW IF EXISTS product_summary;
CREATE VIEW product_summary AS SELECT p.product_id, p.product_name, p.category, p.subcategory, p.brand, COALESCE(SUM(i.quantity), 0) AS units_sold, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS revenue FROM products p LEFT JOIN order_items i ON i.product_id = p.product_id GROUP BY p.product_id, p.product_name, p.category, p.subcategory, p.brand;

DROP VIEW IF EXISTS order_summary;
CREATE VIEW order_summary AS SELECT o.order_id, o.customer_id, o.order_date, o.status, o.region_code, o.payment_method, COUNT(i.item_id) AS line_items, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS order_value FROM orders o LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY o.order_id, o.customer_id, o.order_date, o.status, o.region_code, o.payment_method;

DROP VIEW IF EXISTS revenue_summary;
CREATE VIEW revenue_summary AS SELECT ROUND(SUM(quantity * unit_price * (1 - discount_percent / 100.0)), 2) AS total_revenue, SUM(quantity) AS units_sold, COUNT(DISTINCT order_id) AS orders_with_items FROM order_items;

DROP VIEW IF EXISTS monthly_sales;
CREATE VIEW monthly_sales AS SELECT strftime('%Y-%m', o.order_date) AS sales_month, COUNT(DISTINCT o.order_id) AS order_count, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY strftime('%Y-%m', o.order_date);

DROP VIEW IF EXISTS customer_revenue;
CREATE VIEW customer_revenue AS SELECT c.customer_id, c.customer_name, COALESCE(o.region_code, 'NO_ORDERS') AS region_code, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS revenue FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name, COALESCE(o.region_code, 'NO_ORDERS');
