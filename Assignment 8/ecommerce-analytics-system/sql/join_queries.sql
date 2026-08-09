-- Customer reports use INNER JOIN for customers with activity and LEFT JOIN to retain customers without activity.
-- report: top_customers_by_revenue
SELECT c.customer_id, c.customer_name, c.customer_type, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue
FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id
GROUP BY c.customer_id, c.customer_name, c.customer_type ORDER BY revenue DESC LIMIT 10;

-- report: top_customers_by_orders
SELECT c.customer_id, c.customer_name, COUNT(DISTINCT o.order_id) AS order_count
FROM customers c JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.customer_id, c.customer_name ORDER BY order_count DESC LIMIT 10;

-- report: highest_customer_aov
WITH totals AS (SELECT o.customer_id, o.order_id, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS order_value FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY o.customer_id, o.order_id)
SELECT c.customer_id, c.customer_name, ROUND(AVG(t.order_value), 2) AS average_order_value FROM totals t JOIN customers c ON c.customer_id = t.customer_id GROUP BY c.customer_id, c.customer_name ORDER BY average_order_value DESC LIMIT 10;

-- report: inactive_customers
SELECT c.customer_id, c.customer_name, c.registration_date FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.customer_id, c.customer_name, c.registration_date HAVING MAX(date(o.order_date)) < date('now', '-90 days') ORDER BY c.registration_date;

-- report: customers_without_orders
SELECT c.customer_id, c.customer_name, c.customer_type FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id WHERE o.order_id IS NULL ORDER BY c.customer_id;

-- report: repeat_customers
SELECT c.customer_id, c.customer_name, COUNT(DISTINCT o.order_id) AS order_count FROM customers c JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.customer_id, c.customer_name HAVING COUNT(DISTINCT o.order_id) > 1 ORDER BY order_count DESC;

-- report: vip_customer_revenue
SELECT ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS vip_revenue FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id WHERE c.customer_type = 'VIP';

-- report: customer_lifetime_value
SELECT c.customer_id, c.customer_name, COUNT(DISTINCT o.order_id) AS orders, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS lifetime_value
FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name ORDER BY lifetime_value DESC;

-- report: product_revenue_detail
SELECT p.product_id, p.product_name, p.brand, COALESCE(SUM(i.quantity), 0) AS units_sold, ROUND(COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0), 2) AS revenue
FROM products p LEFT JOIN order_items i ON i.product_id = p.product_id GROUP BY p.product_id, p.product_name, p.brand ORDER BY revenue DESC;

-- report: products_never_ordered
SELECT p.product_id, p.product_name, p.category FROM products p LEFT JOIN order_items i ON i.product_id = p.product_id WHERE i.item_id IS NULL ORDER BY p.product_id;

-- report: orders_by_region
SELECT COALESCE(region_code, 'UNKNOWN') AS region_code, COUNT(*) AS orders FROM orders GROUP BY COALESCE(region_code, 'UNKNOWN') ORDER BY orders DESC;

-- report: top_customers_per_region
WITH customer_region_revenue AS (SELECT o.region_code, c.customer_id, c.customer_name, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue, ROW_NUMBER() OVER (PARTITION BY o.region_code ORDER BY SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) DESC) AS rank_in_region FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id GROUP BY o.region_code, c.customer_id, c.customer_name)
SELECT region_code, customer_id, customer_name, ROUND(revenue, 2) AS revenue FROM customer_region_revenue WHERE rank_in_region <= 3 ORDER BY region_code, revenue DESC;

-- report: top_products_per_region
WITH product_region_revenue AS (SELECT o.region_code, p.product_id, p.product_name, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue, ROW_NUMBER() OVER (PARTITION BY o.region_code ORDER BY SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) DESC) AS rank_in_region FROM orders o JOIN order_items i ON i.order_id = o.order_id JOIN products p ON p.product_id = i.product_id GROUP BY o.region_code, p.product_id, p.product_name)
SELECT region_code, product_id, product_name, ROUND(revenue, 2) AS revenue FROM product_region_revenue WHERE rank_in_region <= 3 ORDER BY region_code, revenue DESC;
