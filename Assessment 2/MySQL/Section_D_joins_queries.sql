USE sales_assignment;

SELECT o.id, c.customer_name, o.order_date, o.region, o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
ORDER BY o.id;

SELECT oi.id, o.id AS order_id, p.product_name, oi.quantity, oi.unit_price
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
ORDER BY oi.id;

SELECT c.customer_name, SUM(o.total_amount) AS total_spend
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.customer_name
ORDER BY total_spend DESC;
