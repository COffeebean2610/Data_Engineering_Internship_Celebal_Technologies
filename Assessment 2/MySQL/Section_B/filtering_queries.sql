USE sales_assignment;

SELECT *
FROM orders
WHERE region = 'North'
ORDER BY order_date;

SELECT *
FROM products
WHERE category = 'Electronics' AND unit_price > 50
ORDER BY unit_price DESC;

SELECT *
FROM orders
WHERE total_amount > 200
ORDER BY total_amount DESC;

SELECT *
FROM customers
WHERE signup_date < '2023-06-01'
ORDER BY signup_date;
