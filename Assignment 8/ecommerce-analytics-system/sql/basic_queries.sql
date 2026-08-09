-- Basic KPI queries. Revenue is discounted line revenue: quantity * unit price * (1 - discount/100).
-- report: total_revenue
SELECT ROUND(SUM(quantity * unit_price * (1 - discount_percent / 100.0)), 2) AS total_revenue FROM order_items;

-- report: total_orders
SELECT COUNT(*) AS total_orders FROM orders;

-- report: total_customers
SELECT COUNT(*) AS total_customers FROM customers;

-- report: average_order_value
WITH order_totals AS (SELECT order_id, SUM(quantity * unit_price * (1 - discount_percent / 100.0)) AS revenue FROM order_items GROUP BY order_id)
SELECT ROUND(AVG(revenue), 2) AS average_order_value FROM order_totals;

-- report: average_revenue_per_customer
SELECT ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) / NULLIF(COUNT(DISTINCT o.customer_id), 0), 2) AS average_revenue_per_customer
FROM orders o JOIN order_items i ON i.order_id = o.order_id;

-- report: total_products_sold
SELECT SUM(quantity) AS total_products_sold FROM order_items;

-- report: total_returned_items
SELECT COALESCE(SUM(i.quantity), 0) AS total_returned_items FROM orders o JOIN order_items i ON i.order_id = o.order_id WHERE o.status = 'RETURNED';

-- report: total_cancelled_orders
SELECT COUNT(*) AS total_cancelled_orders FROM orders WHERE status = 'CANCELLED';
