USE sales_assignment;

INSERT INTO customers (id, customer_name, city, region, signup_date) VALUES
(1, 'Alice Johnson', 'Chicago', 'North', '2023-01-10'),
(2, 'Bob Smith', 'Dallas', 'South', '2023-02-15'),
(3, 'Catherine Lee', 'Austin', 'West', '2023-03-20'),
(4, 'David Chen', 'Boston', 'East', '2023-04-05'),
(5, 'Eva Patel', 'Denver', 'North', '2023-05-12'),
(6, 'Frank Moore', 'Phoenix', 'South', '2023-06-01'),
(7, 'Grace Kim', 'Seattle', 'West', '2023-07-14'),
(8, 'Henry Rivera', 'Miami', 'East', '2023-08-22'),
(9, 'Ivy Brooks', 'Atlanta', 'North', '2023-09-18'),
(10, 'Jack Turner', 'San Diego', 'South', '2023-10-09');

INSERT INTO products (id, product_name, category, unit_price) VALUES
(1, 'Laptop', 'Electronics', 999.99),
(2, 'Wireless Mouse', 'Electronics', 49.99),
(3, 'Coffee Maker', 'Home', 79.95),
(4, 'Desk Lamp', 'Home', 39.99),
(5, 'Running Shoes', 'Sports', 89.99),
(6, 'Backpack', 'Sports', 59.99),
(7, 'Winter Jacket', 'Fashion', 129.99),
(8, 'Leather Wallet', 'Fashion', 49.99);

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
