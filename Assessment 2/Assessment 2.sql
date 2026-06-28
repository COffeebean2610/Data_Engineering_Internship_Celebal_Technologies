/* Create Table/Database*/

CREATE DATABASE IF NOT EXISTS sales_assignment;
-- Query OK, 1 row affected, 1 warning (0.01 sec)

USE sales_assignment;
-- Database changed



CREATE TABLE customers (
    id INT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL
);
--  Query OK, 0 rows affected (0.03 sec)

CREATE TABLE products (
    id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);
-- Query OK, 0 rows affected (0.03 sec)

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    region VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
-- Query OK, 0 rows affected (0.04 sec)

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
-- Query OK, 0 rows affected (0.04 sec)

CREATE INDEX idx_orders_customer ON orders(customer_id);
-- Query OK, 0 rows affected (0.04 sec)
CREATE INDEX idx_orders_date ON orders(order_date);
-- Query OK, 0 rows affected (0.02 sec)
CREATE INDEX idx_order_items_order ON order_items(order_id);
-- Query OK, 0 rows affected (0.02 sec)
CREATE INDEX idx_order_items_product ON order_items(product_id);
-- Query OK, 0 rows affected (0.03 sec)

/*Insert Data*/
USE sales_assignment;
--  Database changed

INSERT INTO customers (id, customer_name, city, region, signup_date) VALUES
(1, 'Aarti Sharma', 'Chicago', 'North', '2023-01-10'),
(2, 'Rohit Kumar', 'Dallas', 'South', '2023-02-15'),
(3, 'Sneha Gupta', 'Austin', 'West', '2023-03-20'),
(4, 'Vikram Patel', 'Boston', 'East', '2023-04-05'),
(5, 'Anjali Patel', 'Denver', 'North', '2023-05-12'),
(6, 'Amit Singh', 'Phoenix', 'South', '2023-06-01'),
(7, 'Priya Reddy', 'Seattle', 'West', '2023-07-14'),
(8, 'Siddharth Rao', 'Miami', 'East', '2023-08-22'),
(9, 'Kavya Nair', 'Atlanta', 'North', '2023-09-18'),
(10, 'Arjun Verma', 'San Diego', 'South', '2023-10-09');
--  Query OK, 10 rows affected (0.02 sec)

INSERT INTO products (id, product_name, category, unit_price) VALUES
(1, 'Laptop', 'Electronics', 999.99),
(2, 'Wireless Mouse', 'Electronics', 49.99),
(3, 'Coffee Maker', 'Home', 79.95),
(4, 'Desk Lamp', 'Home', 39.99),
(5, 'Running Shoes', 'Sports', 89.99),
(6, 'Backpack', 'Sports', 59.99),
(7, 'Winter Jacket', 'Fashion', 129.99),
(8, 'Leather Wallet', 'Fashion', 49.99);
--  Query OK, 8 rows affected (0.01 sec)

INSERT INTO orders (id, customer_id, order_date, region, total_amount) VALUES
(1, 1, '2024-01-05', 'North', 1049.98),
(2, 2, '2024-01-12', 'South', 249.95),
(3, 1, '2024-02-03', 'North', 89.98),
(4, 3, '2024-02-18', 'West', 299.97),
(5, 4, '2024-03-07', 'East', 159.98),
(6, 5, '2024-03-20', 'North', 149.95),
(7, 6, '2024-04-02', 'South', 279.90),
(8, 7, '2024-04-12', 'West', 349.95),
(9, 8, '2024-05-01', 'East', 199.90),
(10, 9, '2024-05-15', 'North', 239.85),
(11, 10, '2024-06-01', 'South', 129.95),
(12, 2, '2024-06-20', 'South', 89.98);
--  Query OK, 12 rows affected (0.01 sec)

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1, 999.99),
(2, 1, 2, 1, 49.99),
(3, 2, 3, 1, 79.95),
(4, 2, 4, 1, 39.99),
(5, 2, 5, 1, 129.99),
(6, 3, 6, 1, 59.99),
(7, 4, 7, 1, 129.99),
(8, 4, 8, 1, 49.99),
(9, 4, 5, 1, 89.99),
(10, 5, 4, 1, 39.99),
(11, 5, 6, 1, 59.99),
(12, 6, 5, 1, 89.99),
(13, 7, 3, 2, 79.95),
(14, 8, 7, 1, 129.99),
(15, 8, 8, 1, 49.99),
(16, 9, 2, 2, 49.99),
(17, 10, 1, 1, 999.99),
(18, 10, 4, 1, 39.99),
(19, 11, 6, 1, 59.99),
(20, 12, 3, 1, 79.95);
--  Query OK, 20 rows affected (0.02 sec)


/* Section_A_basic_queries.sql */

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

/* Setup

mysql> CREATE DATABASE IF NOT EXISTS sales_assignment;
Query OK, 1 row affected, 1 warning (0.01 sec)

mysql> USE sales_assignment;
Database changed
mysql> CREATE TABLE customers (
    ->     id INT PRIMARY KEY,
    ->     customer_name VARCHAR(100) NOT NULL,
    ->     city VARCHAR(100) NOT NULL,
    ->     region VARCHAR(50) NOT NULL,
    ->     signup_date DATE NOT NULL
    -> );
Query OK, 0 rows affected (0.03 sec)

mysql> CREATE TABLE products (
    ->     id INT PRIMARY KEY,
    ->     product_name VARCHAR(100) NOT NULL,
    ->     category VARCHAR(50) NOT NULL,
    ->     unit_price DECIMAL(10,2) NOT NULL
    -> );
Query OK, 0 rows affected (0.03 sec)

mysql> CREATE TABLE orders (
    ->     id INT PRIMARY KEY,
    ->     customer_id INT NOT NULL,
    ->     order_date DATE NOT NULL,
    ->     region VARCHAR(50) NOT NULL,
    ->     total_amount DECIMAL(10,2) NOT NULL,
    ->     FOREIGN KEY (customer_id) REFERENCES customers(id)
    -> );
Query OK, 0 rows affected (0.04 sec)

mysql> CREATE TABLE order_items (
    ->     id INT PRIMARY KEY,
    ->     order_id INT NOT NULL,
    ->     product_id INT NOT NULL,
    ->     quantity INT NOT NULL,
    ->     unit_price DECIMAL(10,2) NOT NULL,
    ->     FOREIGN KEY (order_id) REFERENCES orders(id),
    ->     FOREIGN KEY (product_id) REFERENCES products(id)
    -> );
Query OK, 0 rows affected (0.04 sec)

mysql> CREATE INDEX idx_orders_customer ON orders(customer_id);
Query OK, 0 rows affected (0.04 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> CREATE INDEX idx_orders_date ON orders(order_date);
Query OK, 0 rows affected (0.02 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> CREATE INDEX idx_order_items_order ON order_items(order_id);
Query OK, 0 rows affected (0.02 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> CREATE INDEX idx_order_items_product ON order_items(product_id);
Query OK, 0 rows affected (0.03 sec)
Records: 0  Duplicates: 0  Warnings: 0

Section A

mysql> USE sales_assignment;
Database changed
mysql> INSERT INTO customers (id, customer_name, city, region, signup_date) VALUES
    -> (1, 'Aarti Sharma', 'Chicago', 'North', '2023-01-10'),
    -> (2, 'Rohit Kumar', 'Dallas', 'South', '2023-02-15'),
    -> (3, 'Sneha Gupta', 'Austin', 'West', '2023-03-20'),
    -> (4, 'Vikram Patel', 'Boston', 'East', '2023-04-05'),
    -> (5, 'Anjali Patel', 'Denver', 'North', '2023-05-12'),
    -> (6, 'Amit Singh', 'Phoenix', 'South', '2023-06-01'),
    -> (7, 'Priya Reddy', 'Seattle', 'West', '2023-07-14'),
    -> (8, 'Siddharth Rao', 'Miami', 'East', '2023-08-22'),
    -> (9, 'Kavya Nair', 'Atlanta', 'North', '2023-09-18'),
    -> (10, 'Arjun Verma', 'San Diego', 'South', '2023-10-09');
Query OK, 10 rows affected (0.02 sec)
Records: 10  Duplicates: 0  Warnings: 0

mysql> INSERT INTO products (id, product_name, category, unit_price) VALUES
    -> (1, 'Laptop', 'Electronics', 999.99),
    -> (2, 'Wireless Mouse', 'Electronics', 49.99),
    -> (3, 'Coffee Maker', 'Home', 79.95),
    -> (4, 'Desk Lamp', 'Home', 39.99),
    -> (5, 'Running Shoes', 'Sports', 89.99),
    -> (6, 'Backpack', 'Sports', 59.99),
    -> (7, 'Winter Jacket', 'Fashion', 129.99),
    -> (8, 'Leather Wallet', 'Fashion', 49.99);
Query OK, 8 rows affected (0.01 sec)
Records: 8  Duplicates: 0  Warnings: 0

mysql> INSERT INTO orders (id, customer_id, order_date, region, total_amount) VALUES
    -> (1, 1, '2024-01-05', 'North', 1049.98),
    -> (2, 2, '2024-01-12', 'South', 249.95),
    -> (3, 1, '2024-02-03', 'North', 89.98),
    -> (4, 3, '2024-02-18', 'West', 299.97),
    -> (5, 4, '2024-03-07', 'East', 159.98),
    -> (6, 5, '2024-03-20', 'North', 149.95),
    -> (7, 6, '2024-04-02', 'South', 279.90),
    -> (8, 7, '2024-04-12', 'West', 349.95),
    -> (9, 8, '2024-05-01', 'East', 199.90),
    -> (10, 9, '2024-05-15', 'North', 239.85),
    -> (11, 10, '2024-06-01', 'South', 129.95),
    -> (12, 2, '2024-06-20', 'South', 89.98);
Query OK, 12 rows affected (0.01 sec)
Records: 12  Duplicates: 0  Warnings: 0

mysql> INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES
    -> (1, 1, 1, 1, 999.99),
    -> (2, 1, 2, 1, 49.99),
    -> (3, 2, 3, 1, 79.95),
    -> (4, 2, 4, 1, 39.99),
    -> (5, 2, 5, 1, 129.99),
    -> (6, 3, 6, 1, 59.99),
    -> (7, 4, 7, 1, 129.99),
    -> (8, 4, 8, 1, 49.99),
    -> (9, 4, 5, 1, 89.99),
    -> (10, 5, 4, 1, 39.99),
    -> (11, 5, 6, 1, 59.99),
    -> (12, 6, 5, 1, 89.99),
    -> (13, 7, 3, 2, 79.95),
    -> (14, 8, 7, 1, 129.99),
    -> (15, 8, 8, 1, 49.99),
    -> (16, 9, 2, 2, 49.99),
    -> (17, 10, 1, 1, 999.99),
    -> (18, 10, 4, 1, 39.99),
    -> (19, 11, 6, 1, 59.99),
    -> (20, 12, 3, 1, 79.95);
Query OK, 20 rows affected (0.02 sec)
Records: 20  Duplicates: 0  Warnings: 0

mysql> USE sales_assignment;
Database changed
mysql>
mysql> SELECT table_name
    -> FROM information_schema.tables
    -> WHERE table_schema = 'sales_assignment'
    -> ORDER BY table_name;
+-------------+
| TABLE_NAME  |
+-------------+
| customers   |
| order_items |
| orders      |
| products    |
+-------------+
4 rows in set (0.02 sec)

mysql> SELECT * FROM customers ORDER BY id LIMIT 5;
+----+---------------+---------+--------+-------------+
| id | customer_name | city    | region | signup_date |
+----+---------------+---------+--------+-------------+
|  1 | Aarti Sharma  | Chicago | North  | 2023-01-10  |
|  2 | Rohit Kumar   | Dallas  | South  | 2023-02-15  |
|  3 | Sneha Gupta   | Austin  | West   | 2023-03-20  |
|  4 | Vikram Patel  | Boston  | East   | 2023-04-05  |
|  5 | Anjali Patel  | Denver  | North  | 2023-05-12  |
+----+---------------+---------+--------+-------------+
5 rows in set (0.00 sec)

mysql> SELECT * FROM products ORDER BY id LIMIT 5;
+----+----------------+-------------+------------+
| id | product_name   | category    | unit_price |
+----+----------------+-------------+------------+
|  1 | Laptop         | Electronics |     999.99 |
|  2 | Wireless Mouse | Electronics |      49.99 |
|  3 | Coffee Maker   | Home        |      79.95 |
|  4 | Desk Lamp      | Home        |      39.99 |
|  5 | Running Shoes  | Sports      |      89.99 |
+----+----------------+-------------+------------+
5 rows in set (0.00 sec)

mysql> SELECT * FROM orders ORDER BY id LIMIT 5;
+----+-------------+------------+--------+--------------+
| id | customer_id | order_date | region | total_amount |
+----+-------------+------------+--------+--------------+
|  1 |           1 | 2024-01-05 | North  |      1049.98 |
|  2 |           2 | 2024-01-12 | South  |       249.95 |
|  3 |           1 | 2024-02-03 | North  |        89.98 |
|  4 |           3 | 2024-02-18 | West   |       299.97 |
|  5 |           4 | 2024-03-07 | East   |       159.98 |
+----+-------------+------------+--------+--------------+
5 rows in set (0.00 sec)

mysql> SELECT * FROM order_items ORDER BY id LIMIT 5;
+----+----------+------------+----------+------------+
| id | order_id | product_id | quantity | unit_price |
+----+----------+------------+----------+------------+
|  1 |        1 |          1 |        1 |     999.99 |
|  2 |        1 |          2 |        1 |      49.99 |
|  3 |        2 |          3 |        1 |      79.95 |
|  4 |        2 |          4 |        1 |      39.99 |
|  5 |        2 |          5 |        1 |     129.99 |
+----+----------+------------+----------+------------+
5 rows in set (0.00 sec)

mysql> SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
    -> UNION ALL
    -> SELECT 'products', COUNT(*) FROM products
    -> UNION ALL
    -> SELECT 'orders', COUNT(*) FROM orders
    -> UNION ALL
    -> SELECT 'order_items', COUNT(*) FROM order_items;
+-------------+-----------+
| table_name  | row_count |
+-------------+-----------+
| customers   |        10 |
| products    |         8 |
| orders      |        12 |
| order_items |        20 |
+-------------+-----------+
4 rows in set (0.01 sec)

*/


/* Section_B_filtering_queries.sql */

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


/* Section B

mysql> USE sales_assignment;
Database changed
mysql> SELECT *
    -> FROM orders
    -> WHERE region = 'North'
    -> ORDER BY order_date;
+----+-------------+------------+--------+--------------+
| id | customer_id | order_date | region | total_amount |
+----+-------------+------------+--------+--------------+
|  1 |           1 | 2024-01-05 | North  |      1049.98 |
|  3 |           1 | 2024-02-03 | North  |        89.98 |
|  6 |           5 | 2024-03-20 | North  |       149.95 |
| 10 |           9 | 2024-05-15 | North  |       239.85 |
+----+-------------+------------+--------+--------------+
4 rows in set (0.00 sec)

mysql> SELECT *
    -> FROM products
    -> WHERE category = 'Electronics' AND unit_price > 50
    -> ORDER BY unit_price DESC;
+----+--------------+-------------+------------+
| id | product_name | category    | unit_price |
+----+--------------+-------------+------------+
|  1 | Laptop       | Electronics |     999.99 |
+----+--------------+-------------+------------+
1 row in set (0.00 sec)

mysql> SELECT *
    -> FROM orders
    -> WHERE total_amount > 200
    -> ORDER BY total_amount DESC;
+----+-------------+------------+--------+--------------+
| id | customer_id | order_date | region | total_amount |
+----+-------------+------------+--------+--------------+
|  1 |           1 | 2024-01-05 | North  |      1049.98 |
|  8 |           7 | 2024-04-12 | West   |       349.95 |
|  4 |           3 | 2024-02-18 | West   |       299.97 |
|  7 |           6 | 2024-04-02 | South  |       279.90 |
|  2 |           2 | 2024-01-12 | South  |       249.95 |
| 10 |           9 | 2024-05-15 | North  |       239.85 |
+----+-------------+------------+--------+--------------+
6 rows in set (0.00 sec)

mysql> SELECT *
    -> FROM customers
    -> WHERE signup_date < '2023-06-01'
    -> ORDER BY signup_date;
+----+---------------+---------+--------+-------------+
| id | customer_name | city    | region | signup_date |
+----+---------------+---------+--------+-------------+
|  1 | Aarti Sharma  | Chicago | North  | 2023-01-10  |
|  2 | Rohit Kumar   | Dallas  | South  | 2023-02-15  |
|  3 | Sneha Gupta   | Austin  | West   | 2023-03-20  |
|  4 | Vikram Patel  | Boston  | East   | 2023-04-05  |
|  5 | Anjali Patel  | Denver  | North  | 2023-05-12  |
+----+---------------+---------+--------+-------------+
5 rows in set (0.00 sec)


*/

/* Section_C_aggregation_queries.sql */

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

/* 
Section C


mysql> USE sales_assignment;
Database changed
mysql> SELECT region, SUM(total_amount) AS total_sales
    -> FROM orders
    -> GROUP BY region
    -> ORDER BY total_sales DESC;
+--------+-------------+
| region | total_sales |
+--------+-------------+
| North  |     1529.76 |
| South  |      749.78 |
| West   |      649.92 |
| East   |      359.88 |
+--------+-------------+
4 rows in set (0.00 sec)

mysql>
mysql> SELECT p.product_name, SUM(oi.quantity) AS total_quantity
    -> FROM order_items oi
    -> JOIN products p ON oi.product_id = p.id
    -> GROUP BY p.product_name
    -> ORDER BY total_quantity DESC;
+----------------+----------------+
| product_name   | total_quantity |
+----------------+----------------+
| Coffee Maker   |              4 |
| Wireless Mouse |              3 |
| Desk Lamp      |              3 |
| Running Shoes  |              3 |
| Backpack       |              3 |
| Laptop         |              2 |
| Winter Jacket  |              2 |
| Leather Wallet |              2 |
+----------------+----------------+
8 rows in set (0.00 sec)

mysql>
mysql> SELECT c.customer_name, AVG(o.total_amount) AS avg_order_value
    -> FROM orders o
    -> JOIN customers c ON o.customer_id = c.id
    -> GROUP BY c.customer_name
    -> ORDER BY avg_order_value DESC;
+---------------+-----------------+
| customer_name | avg_order_value |
+---------------+-----------------+
| Aarti Sharma  |      569.980000 |
| Priya Reddy   |      349.950000 |
| Sneha Gupta   |      299.970000 |
| Amit Singh    |      279.900000 |
| Kavya Nair    |      239.850000 |
| Siddharth Rao |      199.900000 |
| Rohit Kumar   |      169.965000 |
| Vikram Patel  |      159.980000 |
| Anjali Patel  |      149.950000 |
| Arjun Verma   |      129.950000 |
+---------------+-----------------+
10 rows in set (0.00 sec)

mysql>
mysql> SELECT category, MAX(unit_price) AS max_unit_price
    -> FROM products
    -> GROUP BY category;
+-------------+----------------+
| category    | max_unit_price |
+-------------+----------------+
| Electronics |         999.99 |
| Home        |          79.95 |
| Sports      |          89.99 |
| Fashion     |         129.99 |
+-------------+----------------+
4 rows in set (0.00 sec)


*/

/* Section_D_joins_queries.sql */

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


/*
Section D


mysql> USE sales_assignment;
Database changed
mysql>
mysql> SELECT o.id, c.customer_name, o.order_date, o.region, o.total_amount
    -> FROM orders o
    -> JOIN customers c ON o.customer_id = c.id
    -> ORDER BY o.id;
+----+---------------+------------+--------+--------------+
| id | customer_name | order_date | region | total_amount |
+----+---------------+------------+--------+--------------+
|  1 | Aarti Sharma  | 2024-01-05 | North  |      1049.98 |
|  2 | Rohit Kumar   | 2024-01-12 | South  |       249.95 |
|  3 | Aarti Sharma  | 2024-02-03 | North  |        89.98 |
|  4 | Sneha Gupta   | 2024-02-18 | West   |       299.97 |
|  5 | Vikram Patel  | 2024-03-07 | East   |       159.98 |
|  6 | Anjali Patel  | 2024-03-20 | North  |       149.95 |
|  7 | Amit Singh    | 2024-04-02 | South  |       279.90 |
|  8 | Priya Reddy   | 2024-04-12 | West   |       349.95 |
|  9 | Siddharth Rao | 2024-05-01 | East   |       199.90 |
| 10 | Kavya Nair    | 2024-05-15 | North  |       239.85 |
| 11 | Arjun Verma   | 2024-06-01 | South  |       129.95 |
| 12 | Rohit Kumar   | 2024-06-20 | South  |        89.98 |
+----+---------------+------------+--------+--------------+
12 rows in set (0.00 sec)

mysql>
mysql> SELECT oi.id, o.id AS order_id, p.product_name, oi.quantity, oi.unit_price
    -> FROM order_items oi
    -> JOIN orders o ON oi.order_id = o.id
    -> JOIN products p ON oi.product_id = p.id
    -> ORDER BY oi.id;
+----+----------+----------------+----------+------------+
| id | order_id | product_name   | quantity | unit_price |
+----+----------+----------------+----------+------------+
|  1 |        1 | Laptop         |        1 |     999.99 |
|  2 |        1 | Wireless Mouse |        1 |      49.99 |
|  3 |        2 | Coffee Maker   |        1 |      79.95 |
|  4 |        2 | Desk Lamp      |        1 |      39.99 |
|  5 |        2 | Running Shoes  |        1 |     129.99 |
|  6 |        3 | Backpack       |        1 |      59.99 |
|  7 |        4 | Winter Jacket  |        1 |     129.99 |
|  8 |        4 | Leather Wallet |        1 |      49.99 |
|  9 |        4 | Running Shoes  |        1 |      89.99 |
| 10 |        5 | Desk Lamp      |        1 |      39.99 |
| 11 |        5 | Backpack       |        1 |      59.99 |
| 12 |        6 | Running Shoes  |        1 |      89.99 |
| 13 |        7 | Coffee Maker   |        2 |      79.95 |
| 14 |        8 | Winter Jacket  |        1 |     129.99 |
| 15 |        8 | Leather Wallet |        1 |      49.99 |
| 16 |        9 | Wireless Mouse |        2 |      49.99 |
| 17 |       10 | Laptop         |        1 |     999.99 |
| 18 |       10 | Desk Lamp      |        1 |      39.99 |
| 19 |       11 | Backpack       |        1 |      59.99 |
| 20 |       12 | Coffee Maker   |        1 |      79.95 |
+----+----------+----------------+----------+------------+
20 rows in set (0.00 sec)

mysql>
mysql> SELECT c.customer_name, SUM(o.total_amount) AS total_spend
    -> FROM customers c
    -> LEFT JOIN orders o ON c.id = o.customer_id
    -> GROUP BY c.customer_name
    -> ORDER BY total_spend DESC;
+---------------+-------------+
| customer_name | total_spend |
+---------------+-------------+
| Aarti Sharma  |     1139.96 |
| Priya Reddy   |      349.95 |
| Rohit Kumar   |      339.93 |
| Sneha Gupta   |      299.97 |
| Amit Singh    |      279.90 |
| Kavya Nair    |      239.85 |
| Siddharth Rao |      199.90 |
| Vikram Patel  |      159.98 |
| Anjali Patel  |      149.95 |
| Arjun Verma   |      129.95 |
+---------------+-------------+
10 rows in set (0.00 sec)


*/

/* Section E_subqueries_queries.sql */

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

/*
Section E

mysql> USE sales_assignment;
Database changed
mysql>
mysql> SELECT DATE_FORMAT(order_date, '%Y-%m') AS month, SUM(total_amount) AS monthly_sales
    -> FROM orders
    -> GROUP BY DATE_FORMAT(order_date, '%Y-%m')
    -> ORDER BY month;
+---------+---------------+
| month   | monthly_sales |
+---------+---------------+
| 2024-01 |       1299.93 |
| 2024-02 |        389.95 |
| 2024-03 |        309.93 |
| 2024-04 |        629.85 |
| 2024-05 |        439.75 |
| 2024-06 |        219.93 |
+---------+---------------+
6 rows in set (0.00 sec)

mysql>
mysql> SELECT c.customer_name, SUM(o.total_amount) AS total_spend
    -> FROM customers c
    -> JOIN orders o ON c.id = o.customer_id
    -> GROUP BY c.customer_name
    -> ORDER BY total_spend DESC
    -> LIMIT 3;
+---------------+-------------+
| customer_name | total_spend |
+---------------+-------------+
| Aarti Sharma  |     1139.96 |
| Priya Reddy   |      349.95 |
| Rohit Kumar   |      339.93 |
+---------------+-------------+
3 rows in set (0.00 sec)

mysql>
mysql> SELECT customer_id, order_date, COUNT(*) AS duplicate_count
    -> FROM orders
    -> GROUP BY customer_id, order_date
    -> HAVING COUNT(*) > 1;
Empty set (0.00 sec)

mysql>
mysql> SELECT id, total_amount,
    ->        CASE
    ->            WHEN total_amount >= 300 THEN 'High Value'
    ->            WHEN total_amount >= 150 THEN 'Medium Value'
    ->            ELSE 'Low Value'
    ->        END AS value_category
    -> FROM orders
    -> ORDER BY total_amount DESC;
+----+--------------+----------------+
| id | total_amount | value_category |
+----+--------------+----------------+
|  1 |      1049.98 | High Value     |
|  8 |       349.95 | High Value     |
|  4 |       299.97 | Medium Value   |
|  7 |       279.90 | Medium Value   |
|  2 |       249.95 | Medium Value   |
| 10 |       239.85 | Medium Value   |
|  9 |       199.90 | Medium Value   |
|  5 |       159.98 | Medium Value   |
|  6 |       149.95 | Low Value      |
| 11 |       129.95 | Low Value      |
|  3 |        89.98 | Low Value      |
| 12 |        89.98 | Low Value      |
+----+--------------+----------------+
12 rows in set (0.00 sec)
*/