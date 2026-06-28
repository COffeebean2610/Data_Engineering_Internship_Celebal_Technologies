Windows PowerShell

Copyright (C) Microsoft Corporation. All rights reserved.



Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows



PS C:\\Users\\Lenovo> mysql -u root -p

Enter password: \*\*\*\*

Welcome to the MySQL monitor.  Commands end with ; or \\g.

Your MySQL connection id is 17

Server version: 8.0.46 MySQL Community Server - GPL



Copyright (c) 2000, 2026, Oracle and/or its affiliates.



Oracle is a registered trademark of Oracle Corporation and/or its

affiliates. Other names may be trademarks of their respective

owners.



Type 'help;' or '\\h' for help. Type '\\c' to clear the current input statement.



mysql> show databases;

+--------------------+

| Database           |

+--------------------+

| information\_schema |

| mysql              |

| performance\_schema |

| sales\_assignment   |

| sys                |

+--------------------+

5 rows in set (0.00 sec)



# **Setup**



mysql> CREATE DATABASE IF NOT EXISTS sales\_assignment;

Query OK, 1 row affected, 1 warning (0.01 sec)



mysql> USE sales\_assignment;

Database changed

mysql> CREATE TABLE customers (

&#x20;   ->     id INT PRIMARY KEY,

&#x20;   ->     customer\_name VARCHAR(100) NOT NULL,

&#x20;   ->     city VARCHAR(100) NOT NULL,

&#x20;   ->     region VARCHAR(50) NOT NULL,

&#x20;   ->     signup\_date DATE NOT NULL

&#x20;   -> );

Query OK, 0 rows affected (0.03 sec)



mysql> CREATE TABLE products (

&#x20;   ->     id INT PRIMARY KEY,

&#x20;   ->     product\_name VARCHAR(100) NOT NULL,

&#x20;   ->     category VARCHAR(50) NOT NULL,

&#x20;   ->     unit\_price DECIMAL(10,2) NOT NULL

&#x20;   -> );

Query OK, 0 rows affected (0.03 sec)



mysql> CREATE TABLE orders (

&#x20;   ->     id INT PRIMARY KEY,

&#x20;   ->     customer\_id INT NOT NULL,

&#x20;   ->     order\_date DATE NOT NULL,

&#x20;   ->     region VARCHAR(50) NOT NULL,

&#x20;   ->     total\_amount DECIMAL(10,2) NOT NULL,

&#x20;   ->     FOREIGN KEY (customer\_id) REFERENCES customers(id)

&#x20;   -> );

Query OK, 0 rows affected (0.04 sec)



mysql> CREATE TABLE order\_items (

&#x20;   ->     id INT PRIMARY KEY,

&#x20;   ->     order\_id INT NOT NULL,

&#x20;   ->     product\_id INT NOT NULL,

&#x20;   ->     quantity INT NOT NULL,

&#x20;   ->     unit\_price DECIMAL(10,2) NOT NULL,

&#x20;   ->     FOREIGN KEY (order\_id) REFERENCES orders(id),

&#x20;   ->     FOREIGN KEY (product\_id) REFERENCES products(id)

&#x20;   -> );

Query OK, 0 rows affected (0.04 sec)



mysql> CREATE INDEX idx\_orders\_customer ON orders(customer\_id);

Query OK, 0 rows affected (0.04 sec)

Records: 0  Duplicates: 0  Warnings: 0



mysql> CREATE INDEX idx\_orders\_date ON orders(order\_date);

Query OK, 0 rows affected (0.02 sec)

Records: 0  Duplicates: 0  Warnings: 0



mysql> CREATE INDEX idx\_order\_items\_order ON order\_items(order\_id);

Query OK, 0 rows affected (0.02 sec)

Records: 0  Duplicates: 0  Warnings: 0



mysql> CREATE INDEX idx\_order\_items\_product ON order\_items(product\_id);

Query OK, 0 rows affected (0.03 sec)

Records: 0  Duplicates: 0  Warnings: 0





# **Section A** 



mysql> USE sales\_assignment;

Database changed

mysql> INSERT INTO customers (id, customer\_name, city, region, signup\_date) VALUES

&#x20;   -> (1, 'Alice Johnson', 'Chicago', 'North', '2023-01-10'),

&#x20;   -> (2, 'Bob Smith', 'Dallas', 'South', '2023-02-15'),

&#x20;   -> (3, 'Catherine Lee', 'Austin', 'West', '2023-03-20'),

&#x20;   -> (4, 'David Chen', 'Boston', 'East', '2023-04-05'),

&#x20;   -> (5, 'Eva Patel', 'Denver', 'North', '2023-05-12'),

&#x20;   -> (6, 'Frank Moore', 'Phoenix', 'South', '2023-06-01'),

&#x20;   -> (7, 'Grace Kim', 'Seattle', 'West', '2023-07-14'),

&#x20;   -> (8, 'Henry Rivera', 'Miami', 'East', '2023-08-22'),

&#x20;   -> (9, 'Ivy Brooks', 'Atlanta', 'North', '2023-09-18'),

&#x20;   -> (10, 'Jack Turner', 'San Diego', 'South', '2023-10-09');

Query OK, 10 rows affected (0.02 sec)

Records: 10  Duplicates: 0  Warnings: 0



mysql> INSERT INTO products (id, product\_name, category, unit\_price) VALUES

&#x20;   -> (1, 'Laptop', 'Electronics', 999.99),

&#x20;   -> (2, 'Wireless Mouse', 'Electronics', 49.99),

&#x20;   -> (3, 'Coffee Maker', 'Home', 79.95),

&#x20;   -> (4, 'Desk Lamp', 'Home', 39.99),

&#x20;   -> (5, 'Running Shoes', 'Sports', 89.99),

&#x20;   -> (6, 'Backpack', 'Sports', 59.99),

&#x20;   -> (7, 'Winter Jacket', 'Fashion', 129.99),

&#x20;   -> (8, 'Leather Wallet', 'Fashion', 49.99);

Query OK, 8 rows affected (0.01 sec)

Records: 8  Duplicates: 0  Warnings: 0



mysql> INSERT INTO orders (id, customer\_id, order\_date, region, total\_amount) VALUES

&#x20;   -> (1, 1, '2024-01-05', 'North', 1049.98),

&#x20;   -> (2, 2, '2024-01-12', 'South', 249.95),

&#x20;   -> (3, 1, '2024-02-03', 'North', 89.98),

&#x20;   -> (4, 3, '2024-02-18', 'West', 299.97),

&#x20;   -> (5, 4, '2024-03-07', 'East', 159.98),

&#x20;   -> (6, 5, '2024-03-20', 'North', 149.95),

&#x20;   -> (7, 6, '2024-04-02', 'South', 279.90),

&#x20;   -> (8, 7, '2024-04-12', 'West', 349.95),

&#x20;   -> (9, 8, '2024-05-01', 'East', 199.90),

&#x20;   -> (10, 9, '2024-05-15', 'North', 239.85),

&#x20;   -> (11, 10, '2024-06-01', 'South', 129.95),

&#x20;   -> (12, 2, '2024-06-20', 'South', 89.98);

Query OK, 12 rows affected (0.01 sec)

Records: 12  Duplicates: 0  Warnings: 0



mysql> INSERT INTO order\_items (id, order\_id, product\_id, quantity, unit\_price) VALUES

&#x20;   -> (1, 1, 1, 1, 999.99),

&#x20;   -> (2, 1, 2, 1, 49.99),

&#x20;   -> (3, 2, 3, 1, 79.95),

&#x20;   -> (4, 2, 4, 1, 39.99),

&#x20;   -> (5, 2, 5, 1, 129.99),

&#x20;   -> (6, 3, 6, 1, 59.99),

&#x20;   -> (7, 4, 7, 1, 129.99),

&#x20;   -> (8, 4, 8, 1, 49.99),

&#x20;   -> (9, 4, 5, 1, 89.99),

&#x20;   -> (10, 5, 4, 1, 39.99),

&#x20;   -> (11, 5, 6, 1, 59.99),

&#x20;   -> (12, 6, 5, 1, 89.99),

&#x20;   -> (13, 7, 3, 2, 79.95),

&#x20;   -> (14, 8, 7, 1, 129.99),

&#x20;   -> (15, 8, 8, 1, 49.99),

&#x20;   -> (16, 9, 2, 2, 49.99),

&#x20;   -> (17, 10, 1, 1, 999.99),

&#x20;   -> (18, 10, 4, 1, 39.99),

&#x20;   -> (19, 11, 6, 1, 59.99),

&#x20;   -> (20, 12, 3, 1, 79.95);

Query OK, 20 rows affected (0.02 sec)

Records: 20  Duplicates: 0  Warnings: 0



mysql> USE sales\_assignment;

Database changed

mysql>

mysql> SELECT table\_name

&#x20;   -> FROM information\_schema.tables

&#x20;   -> WHERE table\_schema = 'sales\_assignment'

&#x20;   -> ORDER BY table\_name;

+-------------+

| TABLE\_NAME  |

+-------------+

| customers   |

| order\_items |

| orders      |

| products    |

+-------------+

4 rows in set (0.02 sec)



mysql> SELECT \* FROM customers ORDER BY id LIMIT 5;

+----+---------------+---------+--------+-------------+

| id | customer\_name | city    | region | signup\_date |

+----+---------------+---------+--------+-------------+

|  1 | Alice Johnson | Chicago | North  | 2023-01-10  |

|  2 | Bob Smith     | Dallas  | South  | 2023-02-15  |

|  3 | Catherine Lee | Austin  | West   | 2023-03-20  |

|  4 | David Chen    | Boston  | East   | 2023-04-05  |

|  5 | Eva Patel     | Denver  | North  | 2023-05-12  |

+----+---------------+---------+--------+-------------+

5 rows in set (0.00 sec)



mysql> SELECT \* FROM products ORDER BY id LIMIT 5;

+----+----------------+-------------+------------+

| id | product\_name   | category    | unit\_price |

+----+----------------+-------------+------------+

|  1 | Laptop         | Electronics |     999.99 |

|  2 | Wireless Mouse | Electronics |      49.99 |

|  3 | Coffee Maker   | Home        |      79.95 |

|  4 | Desk Lamp      | Home        |      39.99 |

|  5 | Running Shoes  | Sports      |      89.99 |

+----+----------------+-------------+------------+

5 rows in set (0.00 sec)



mysql> SELECT \* FROM orders ORDER BY id LIMIT 5;

+----+-------------+------------+--------+--------------+

| id | customer\_id | order\_date | region | total\_amount |

+----+-------------+------------+--------+--------------+

|  1 |           1 | 2024-01-05 | North  |      1049.98 |

|  2 |           2 | 2024-01-12 | South  |       249.95 |

|  3 |           1 | 2024-02-03 | North  |        89.98 |

|  4 |           3 | 2024-02-18 | West   |       299.97 |

|  5 |           4 | 2024-03-07 | East   |       159.98 |

+----+-------------+------------+--------+--------------+

5 rows in set (0.00 sec)



mysql> SELECT \* FROM order\_items ORDER BY id LIMIT 5;

+----+----------+------------+----------+------------+

| id | order\_id | product\_id | quantity | unit\_price |

+----+----------+------------+----------+------------+

|  1 |        1 |          1 |        1 |     999.99 |

|  2 |        1 |          2 |        1 |      49.99 |

|  3 |        2 |          3 |        1 |      79.95 |

|  4 |        2 |          4 |        1 |      39.99 |

|  5 |        2 |          5 |        1 |     129.99 |

+----+----------+------------+----------+------------+

5 rows in set (0.00 sec)



mysql> SELECT 'customers' AS table\_name, COUNT(\*) AS row\_count FROM customers

&#x20;   -> UNION ALL

&#x20;   -> SELECT 'products', COUNT(\*) FROM products

&#x20;   -> UNION ALL

&#x20;   -> SELECT 'orders', COUNT(\*) FROM orders

&#x20;   -> UNION ALL

&#x20;   -> SELECT 'order\_items', COUNT(\*) FROM order\_items;

+-------------+-----------+

| table\_name  | row\_count |

+-------------+-----------+

| customers   |        10 |

| products    |         8 |

| orders      |        12 |

| order\_items |        20 |

+-------------+-----------+

4 rows in set (0.01 sec)



# **Section B**



**mysql> USE sales\_assignment;**

**Database changed**

**mysql> SELECT \***

&#x20;   **-> FROM orders**

&#x20;   **-> WHERE region = 'North'**

&#x20;   **-> ORDER BY order\_date;**

**+----+-------------+------------+--------+--------------+**

**| id | customer\_id | order\_date | region | total\_amount |**

**+----+-------------+------------+--------+--------------+**

**|  1 |           1 | 2024-01-05 | North  |      1049.98 |**

**|  3 |           1 | 2024-02-03 | North  |        89.98 |**

**|  6 |           5 | 2024-03-20 | North  |       149.95 |**

**| 10 |           9 | 2024-05-15 | North  |       239.85 |**

**+----+-------------+------------+--------+--------------+**

**4 rows in set (0.00 sec)**



**mysql> SELECT \***

&#x20;   **-> FROM products**

&#x20;   **-> WHERE category = 'Electronics' AND unit\_price > 50**

&#x20;   **-> ORDER BY unit\_price DESC;**

**+----+--------------+-------------+------------+**

**| id | product\_name | category    | unit\_price |**

**+----+--------------+-------------+------------+**

**|  1 | Laptop       | Electronics |     999.99 |**

**+----+--------------+-------------+------------+**

**1 row in set (0.00 sec)**



**mysql> SELECT \***

&#x20;   **-> FROM orders**

&#x20;   **-> WHERE total\_amount > 200**

&#x20;   **-> ORDER BY total\_amount DESC;**

**+----+-------------+------------+--------+--------------+**

**| id | customer\_id | order\_date | region | total\_amount |**

**+----+-------------+------------+--------+--------------+**

**|  1 |           1 | 2024-01-05 | North  |      1049.98 |**

**|  8 |           7 | 2024-04-12 | West   |       349.95 |**

**|  4 |           3 | 2024-02-18 | West   |       299.97 |**

**|  7 |           6 | 2024-04-02 | South  |       279.90 |**

**|  2 |           2 | 2024-01-12 | South  |       249.95 |**

**| 10 |           9 | 2024-05-15 | North  |       239.85 |**

**+----+-------------+------------+--------+--------------+**

**6 rows in set (0.00 sec)**



**mysql> SELECT \***

&#x20;   **-> FROM customers**

&#x20;   **-> WHERE signup\_date < '2023-06-01'**

&#x20;   **-> ORDER BY signup\_date;**

**+----+---------------+---------+--------+-------------+**

**| id | customer\_name | city    | region | signup\_date |**

**+----+---------------+---------+--------+-------------+**

**|  1 | Alice Johnson | Chicago | North  | 2023-01-10  |**

**|  2 | Bob Smith     | Dallas  | South  | 2023-02-15  |**

**|  3 | Catherine Lee | Austin  | West   | 2023-03-20  |**

**|  4 | David Chen    | Boston  | East   | 2023-04-05  |**

**|  5 | Eva Patel     | Denver  | North  | 2023-05-12  |**

**+----+---------------+---------+--------+-------------+**

**5 rows in set (0.00 sec)**





# **Section C**





mysql> USE sales\_assignment;

Database changed

mysql> SELECT region, SUM(total\_amount) AS total\_sales

&#x20;   -> FROM orders

&#x20;   -> GROUP BY region

&#x20;   -> ORDER BY total\_sales DESC;

+--------+-------------+

| region | total\_sales |

+--------+-------------+

| North  |     1529.76 |

| South  |      749.78 |

| West   |      649.92 |

| East   |      359.88 |

+--------+-------------+

4 rows in set (0.00 sec)



mysql>

mysql> SELECT p.product\_name, SUM(oi.quantity) AS total\_quantity

&#x20;   -> FROM order\_items oi

&#x20;   -> JOIN products p ON oi.product\_id = p.id

&#x20;   -> GROUP BY p.product\_name

&#x20;   -> ORDER BY total\_quantity DESC;

+----------------+----------------+

| product\_name   | total\_quantity |

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

mysql> SELECT c.customer\_name, AVG(o.total\_amount) AS avg\_order\_value

&#x20;   -> FROM orders o

&#x20;   -> JOIN customers c ON o.customer\_id = c.id

&#x20;   -> GROUP BY c.customer\_name

&#x20;   -> ORDER BY avg\_order\_value DESC;

+---------------+-----------------+

| customer\_name | avg\_order\_value |

+---------------+-----------------+

| Alice Johnson |      569.980000 |

| Grace Kim     |      349.950000 |

| Catherine Lee |      299.970000 |

| Frank Moore   |      279.900000 |

| Ivy Brooks    |      239.850000 |

| Henry Rivera  |      199.900000 |

| Bob Smith     |      169.965000 |

| David Chen    |      159.980000 |

| Eva Patel     |      149.950000 |

| Jack Turner   |      129.950000 |

+---------------+-----------------+

10 rows in set (0.00 sec)



mysql>

mysql> SELECT category, MAX(unit\_price) AS max\_unit\_price

&#x20;   -> FROM products

&#x20;   -> GROUP BY category;

+-------------+----------------+

| category    | max\_unit\_price |

+-------------+----------------+

| Electronics |         999.99 |

| Home        |          79.95 |

| Sports      |          89.99 |

| Fashion     |         129.99 |

+-------------+----------------+

4 rows in set (0.00 sec)





# **Section D**





mysql> USE sales\_assignment;

Database changed

mysql>

mysql> SELECT o.id, c.customer\_name, o.order\_date, o.region, o.total\_amount

&#x20;   -> FROM orders o

&#x20;   -> JOIN customers c ON o.customer\_id = c.id

&#x20;   -> ORDER BY o.id;

+----+---------------+------------+--------+--------------+

| id | customer\_name | order\_date | region | total\_amount |

+----+---------------+------------+--------+--------------+

|  1 | Alice Johnson | 2024-01-05 | North  |      1049.98 |

|  2 | Bob Smith     | 2024-01-12 | South  |       249.95 |

|  3 | Alice Johnson | 2024-02-03 | North  |        89.98 |

|  4 | Catherine Lee | 2024-02-18 | West   |       299.97 |

|  5 | David Chen    | 2024-03-07 | East   |       159.98 |

|  6 | Eva Patel     | 2024-03-20 | North  |       149.95 |

|  7 | Frank Moore   | 2024-04-02 | South  |       279.90 |

|  8 | Grace Kim     | 2024-04-12 | West   |       349.95 |

|  9 | Henry Rivera  | 2024-05-01 | East   |       199.90 |

| 10 | Ivy Brooks    | 2024-05-15 | North  |       239.85 |

| 11 | Jack Turner   | 2024-06-01 | South  |       129.95 |

| 12 | Bob Smith     | 2024-06-20 | South  |        89.98 |

+----+---------------+------------+--------+--------------+

12 rows in set (0.00 sec)



mysql>

mysql> SELECT oi.id, o.id AS order\_id, p.product\_name, oi.quantity, oi.unit\_price

&#x20;   -> FROM order\_items oi

&#x20;   -> JOIN orders o ON oi.order\_id = o.id

&#x20;   -> JOIN products p ON oi.product\_id = p.id

&#x20;   -> ORDER BY oi.id;

+----+----------+----------------+----------+------------+

| id | order\_id | product\_name   | quantity | unit\_price |

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

mysql> SELECT c.customer\_name, SUM(o.total\_amount) AS total\_spend

&#x20;   -> FROM customers c

&#x20;   -> LEFT JOIN orders o ON c.id = o.customer\_id

&#x20;   -> GROUP BY c.customer\_name

&#x20;   -> ORDER BY total\_spend DESC;

+---------------+-------------+

| customer\_name | total\_spend |

+---------------+-------------+

| Alice Johnson |     1139.96 |

| Grace Kim     |      349.95 |

| Bob Smith     |      339.93 |

| Catherine Lee |      299.97 |

| Frank Moore   |      279.90 |

| Ivy Brooks    |      239.85 |

| Henry Rivera  |      199.90 |

| David Chen    |      159.98 |

| Eva Patel     |      149.95 |

| Jack Turner   |      129.95 |

+---------------+-------------+

10 rows in set (0.00 sec)



**Section E**
===



**mysql> USE sales\_assignment;**

**Database changed**

**mysql>**

**mysql> SELECT DATE\_FORMAT(order\_date, '%Y-%m') AS month, SUM(total\_amount) AS monthly\_sales**

&#x20;   **-> FROM orders**

&#x20;   **-> GROUP BY DATE\_FORMAT(order\_date, '%Y-%m')**

&#x20;   **-> ORDER BY month;**

**+---------+---------------+**

**| month   | monthly\_sales |**

**+---------+---------------+**

**| 2024-01 |       1299.93 |**

**| 2024-02 |        389.95 |**

**| 2024-03 |        309.93 |**

**| 2024-04 |        629.85 |**

**| 2024-05 |        439.75 |**

**| 2024-06 |        219.93 |**

**+---------+---------------+**

**6 rows in set (0.00 sec)**



**mysql>**

**mysql> SELECT c.customer\_name, SUM(o.total\_amount) AS total\_spend**

&#x20;   **-> FROM customers c**

&#x20;   **-> JOIN orders o ON c.id = o.customer\_id**

&#x20;   **-> GROUP BY c.customer\_name**

&#x20;   **-> ORDER BY total\_spend DESC**

&#x20;   **-> LIMIT 3;**

**+---------------+-------------+**

**| customer\_name | total\_spend |**

**+---------------+-------------+**

**| Alice Johnson |     1139.96 |**

**| Grace Kim     |      349.95 |**

**| Bob Smith     |      339.93 |**

**+---------------+-------------+**

**3 rows in set (0.00 sec)**



**mysql>**

**mysql> SELECT customer\_id, order\_date, COUNT(\*) AS duplicate\_count**

&#x20;   **-> FROM orders**

&#x20;   **-> GROUP BY customer\_id, order\_date**

&#x20;   **-> HAVING COUNT(\*) > 1;**

**Empty set (0.00 sec)**



**mysql>**

**mysql> SELECT id, total\_amount,**

&#x20;   **->        CASE**

&#x20;   **->            WHEN total\_amount >= 300 THEN 'High Value'**

&#x20;   **->            WHEN total\_amount >= 150 THEN 'Medium Value'**

&#x20;   **->            ELSE 'Low Value'**

&#x20;   **->        END AS value\_category**

&#x20;   **-> FROM orders**

&#x20;   **-> ORDER BY total\_amount DESC;**

**+----+--------------+----------------+**

**| id | total\_amount | value\_category |**

**+----+--------------+----------------+**

**|  1 |      1049.98 | High Value     |**

**|  8 |       349.95 | High Value     |**

**|  4 |       299.97 | Medium Value   |**

**|  7 |       279.90 | Medium Value   |**

**|  2 |       249.95 | Medium Value   |**

**| 10 |       239.85 | Medium Value   |**

**|  9 |       199.90 | Medium Value   |**

**|  5 |       159.98 | Medium Value   |**

**|  6 |       149.95 | Low Value      |**

**| 11 |       129.95 | Low Value      |**

**|  3 |        89.98 | Low Value      |**

**| 12 |        89.98 | Low Value      |**

**+----+--------------+----------------+**

**12 rows in set (0.00 sec)**



