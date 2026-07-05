-- Assessment 3: Superstore SQL work

-- 1. Create DB and raw table
CREATE DATABASE IF NOT EXISTS superstore_db;
USE superstore_db;

DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS superstore_raw;

CREATE TABLE superstore_raw (
    row_id INT,
    order_id  VARCHAR(50),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),
    customer_id VARCHAR(50),
    customer_name VARCHAR(100),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50),
    product_id VARCHAR(50),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name VARCHAR(255),
    sales DECIMAL(10,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(10,2)
);


-- 2. Create the normalized tables
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    segment VARCHAR(50) NOT NULL
);

INSERT INTO customers (customer_id, customer_name, segment)
SELECT  customer_id,
        MAX(customer_name) AS customer_name,
        MAX(segment) AS segment
FROM   superstore_raw
WHERE  customer_id IS NOT NULL
GROUP BY customer_id;

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL
);

INSERT INTO products (product_id, product_name, category, sub_category)
SELECT  product_id,
        MAX(product_name) AS product_name,
        MAX(category) AS category,
        MAX(sub_category) AS sub_category
FROM   superstore_raw
WHERE  product_id IS NOT NULL
GROUP BY product_id;

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    order_date DATE NOT NULL,
    ship_date DATE,
    customer_id VARCHAR(50) NOT NULL,
    ship_mode VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

INSERT INTO orders (order_id, order_date, ship_date, customer_id, ship_mode)
SELECT order_id,
       STR_TO_DATE(MAX(order_date), '%c/%e/%Y') AS order_date,
       STR_TO_DATE(MAX(ship_date), '%c/%e/%Y') AS ship_date,
       MAX(customer_id) AS customer_id,
       MAX(ship_mode) AS ship_mode
FROM superstore_raw
WHERE order_id IS NOT NULL
GROUP BY order_id;

CREATE TABLE order_details (
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    sales DECIMAL(10,2) NOT NULL CHECK (sales >= 0),
    quantity INT NOT NULL CHECK (quantity > 0),
    discount DECIMAL(5,2) NOT NULL CHECK (discount BETWEEN 0 AND 1),
    profit DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO order_details (order_id, product_id, sales, quantity, discount, profit)
SELECT order_id,
       product_id,
       MAX(sales) AS sales,
       MAX(quantity) AS quantity,
       MAX(discount) AS discount,
       MAX(profit) AS profit
FROM superstore_raw
WHERE order_id IS NOT NULL AND product_id IS NOT NULL
GROUP BY order_id, product_id;

-- 3. Subqueries
-- some basic ones first
SELECT *
FROM order_details
WHERE sales > (SELECT AVG(sales) FROM order_details);

SELECT *
FROM order_details
WHERE sales = (SELECT MAX(sales) FROM order_details);

-- customers above average sales
WITH customer_sales AS (
    SELECT o.customer_id, SUM(od.sales) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
)
SELECT customer_id, total_sales
FROM customer_sales
WHERE total_sales > (
    SELECT AVG(total_sales)
    FROM customer_sales
);

-- 4. CTEs
-- total sales per customer
WITH customer_sales AS (
    SELECT o.customer_id, SUM(od.sales) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
)
SELECT *
FROM customer_sales
ORDER BY total_sales DESC;

-- average sales per customer
WITH customer_sales AS (
    SELECT o.customer_id, SUM(od.sales) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
)
SELECT AVG(total_sales) AS avg_customer_sales
FROM customer_sales;

-- customers above average
WITH customer_sales AS (
    SELECT o.customer_id, SUM(od.sales) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
)
SELECT customer_id, total_sales
FROM customer_sales
WHERE total_sales > (
    SELECT AVG(total_sales)
    FROM customer_sales
)
ORDER BY total_sales DESC;

-- 5. Window functions
-- ranking customers by sales
WITH customer_sales AS (
    SELECT o.customer_id, SUM(od.sales) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
)
SELECT customer_id,
       total_sales,
       ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS row_num,
       RANK() OVER (ORDER BY total_sales DESC) AS sales_rank,
       DENSE_RANK() OVER (ORDER BY total_sales DESC) AS dense_sales_rank
FROM customer_sales;

-- latest order per customer
SELECT customer_id, order_id, order_date,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS latest_order_rank
FROM orders;

-- highest order value per customer
WITH customer_order_sales AS (
    SELECT o.customer_id, o.order_id, SUM(od.sales) AS order_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id, o.order_id
)
SELECT customer_id, order_id, order_sales,
       RANK() OVER (PARTITION BY customer_id ORDER BY order_sales DESC) AS order_rank
FROM customer_order_sales;

-- 6. Join and analysis
-- sales by category
SELECT c.customer_name,
       p.category,
       SUM(od.sales) AS total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
JOIN products p ON od.product_id = p.product_id
GROUP BY c.customer_name, p.category
ORDER BY total_sales DESC;

-- 8. Customer insights
-- overall customer ranking
WITH customer_metrics AS (
    SELECT o.customer_id,
           SUM(od.sales) AS total_sales,
           SUM(od.profit) AS total_profit,
           COUNT(DISTINCT o.order_id) AS total_orders
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
), ranked_customers AS (
    SELECT c.customer_name,
           c.customer_id,
           c.segment,
           cm.total_sales,
           cm.total_profit,
           cm.total_orders,
           RANK() OVER (ORDER BY cm.total_sales DESC) AS sales_rank
    FROM customer_metrics cm
    JOIN customers c ON cm.customer_id = c.customer_id
)
SELECT customer_name, customer_id, segment, total_sales, total_profit, total_orders, sales_rank
FROM ranked_customers
ORDER BY sales_rank;

-- top 10 customers
WITH customer_metrics AS (
    SELECT o.customer_id,
           SUM(od.sales) AS total_sales,
           SUM(od.profit) AS total_profit,
           COUNT(DISTINCT o.order_id) AS total_orders
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
), ranked_customers AS (
    SELECT c.customer_name,
           c.customer_id,
           c.segment,
           cm.total_sales,
           cm.total_profit,
           cm.total_orders,
           RANK() OVER (ORDER BY cm.total_sales DESC) AS sales_rank
    FROM customer_metrics cm
    JOIN customers c ON cm.customer_id = c.customer_id
)
SELECT *
FROM ranked_customers
WHERE sales_rank <= 10
ORDER BY sales_rank;

-- bottom 10 customers
WITH customer_metrics AS (
    SELECT o.customer_id,
           SUM(od.sales) AS total_sales,
           SUM(od.profit) AS total_profit,
           COUNT(DISTINCT o.order_id) AS total_orders
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
), ranked_customers AS (
    SELECT c.customer_name,
           c.customer_id,
           c.segment,
           cm.total_sales,
           cm.total_profit,
           cm.total_orders,
           RANK() OVER (ORDER BY cm.total_sales ASC) AS sales_rank
    FROM customer_metrics cm
    JOIN customers c ON cm.customer_id = c.customer_id
)
SELECT *
FROM ranked_customers
WHERE sales_rank <= 10
ORDER BY sales_rank;

-- customers with only one order
SELECT c.customer_name, c.customer_id, COUNT(DISTINCT o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name, c.customer_id
HAVING COUNT(DISTINCT o.order_id) = 1;

-- highest profit customer
SELECT c.customer_name, c.customer_id, SUM(od.profit) AS total_profit
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.customer_name, c.customer_id
ORDER BY total_profit DESC
LIMIT 1;

-- highest quantity customer
SELECT c.customer_name, c.customer_id, SUM(od.quantity) AS total_quantity
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.customer_name, c.customer_id
ORDER BY total_quantity DESC
LIMIT 1;

-- Most valuable customer in each segment
WITH segment_customer_sales AS (
    SELECT c.segment,
           c.customer_id,
           SUM(od.sales) AS total_sales
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY c.segment, c.customer_id
), ranked_segment_customers AS (
    SELECT segment,
           customer_id,
           total_sales,
           RANK() OVER (PARTITION BY segment ORDER BY total_sales DESC) AS sales_rank
    FROM segment_customer_sales
)
SELECT segment, customer_id, total_sales, sales_rank
FROM ranked_segment_customers
WHERE sales_rank = 1;

-- Top customer in every category
WITH category_customer_sales AS (
    SELECT p.category,
           c.customer_id,
           SUM(od.sales) AS total_sales
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_details od ON o.order_id = od.order_id
    JOIN products p ON od.product_id = p.product_id
    GROUP BY p.category, c.customer_id
), ranked_category_customers AS (
    SELECT category,
           customer_id,
           total_sales,
           RANK() OVER (PARTITION BY category ORDER BY total_sales DESC) AS sales_rank
    FROM category_customer_sales
)
SELECT category, customer_id, total_sales, sales_rank
FROM ranked_category_customers
WHERE sales_rank = 1;

-- sales distribution using NTILE
WITH customer_metrics AS (
    SELECT o.customer_id,
           SUM(od.sales) AS total_sales
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.customer_id
), sales_buckets AS (
    SELECT customer_id,
           total_sales,
           NTILE(4) OVER (ORDER BY total_sales DESC) AS quartile
    FROM customer_metrics
)
SELECT quartile,
       CASE
           WHEN quartile = 1 THEN 'High'
           WHEN quartile = 2 THEN 'Medium-High'
           WHEN quartile = 3 THEN 'Medium-Low'
           ELSE 'Low'
       END AS sales_bucket,
       COUNT(*) AS customer_count,
       MIN(total_sales) AS min_sales,
       MAX(total_sales) AS max_sales
FROM sales_buckets
GROUP BY quartile
ORDER BY quartile;

-- business insights
-- category performance
SELECT p.category,
       SUM(od.sales) AS total_sales,
       SUM(od.profit) AS total_profit
FROM products p
JOIN order_details od ON p.product_id = od.product_id
GROUP BY p.category
ORDER BY total_sales DESC;

-- Segment performance
SELECT c.segment,
       SUM(od.sales) AS total_sales,
       SUM(od.profit) AS total_profit,
       COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.segment
ORDER BY total_sales DESC;
