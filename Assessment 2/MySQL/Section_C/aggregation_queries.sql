USE sales_assignment;

SELECT region, SUM(total_amount) AS total_sales
FROM orders
GROUP BY region
ORDER BY total_sales DESC;

SELECT p.product_name, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.product_name
ORDER BY total_quantity DESC;

SELECT c.customer_name, AVG(o.total_amount) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.customer_name
ORDER BY avg_order_value DESC;

SELECT category, MAX(unit_price) AS max_unit_price
FROM products
GROUP BY category;
