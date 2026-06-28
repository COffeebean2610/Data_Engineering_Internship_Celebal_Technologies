USE sales_assignment;

SELECT DATE_FORMAT(order_date, '%Y-%m') AS month, SUM(total_amount) AS monthly_sales
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

SELECT c.customer_name, SUM(o.total_amount) AS total_spend
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.customer_name
ORDER BY total_spend DESC
LIMIT 3;

SELECT customer_id, order_date, COUNT(*) AS duplicate_count
FROM orders
GROUP BY customer_id, order_date
HAVING COUNT(*) > 1;

SELECT id, total_amount,
       CASE
           WHEN total_amount >= 300 THEN 'High Value'
           WHEN total_amount >= 150 THEN 'Medium Value'
           ELSE 'Low Value'
       END AS value_category
FROM orders
ORDER BY total_amount DESC;
