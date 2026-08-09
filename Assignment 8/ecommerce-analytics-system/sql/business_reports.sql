-- Advanced business reports: CTEs, subqueries, CASE, COALESCE, NULLIF, casts, and SQLite date functions.
-- report: highest_profit_category
SELECT category, ROUND(SUM((i.unit_price * (1 - i.discount_percent / 100.0) - p.cost_price) * i.quantity), 2) AS gross_profit FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY category ORDER BY gross_profit DESC LIMIT 1;

-- report: lowest_profit_category
SELECT category, ROUND(SUM((i.unit_price * (1 - i.discount_percent / 100.0) - p.cost_price) * i.quantity), 2) AS gross_profit FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY category ORDER BY gross_profit ASC LIMIT 1;

-- report: average_customer_order_lead_time
SELECT ROUND(AVG(julianday(o.order_date) - julianday(c.registration_date)), 2) AS average_days_from_registration_to_order FROM orders o JOIN customers c ON c.customer_id = o.customer_id WHERE julianday(o.order_date) >= julianday(c.registration_date);

-- report: revenue_per_day
SELECT date(o.order_date) AS sales_day, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY date(o.order_date) ORDER BY sales_day;

-- report: revenue_per_week
SELECT strftime('%Y-W%W', o.order_date) AS sales_week, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY strftime('%Y-W%W', o.order_date) ORDER BY sales_week;

-- report: revenue_per_month
SELECT strftime('%Y-%m', o.order_date) AS sales_month, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY strftime('%Y-%m', o.order_date) ORDER BY sales_month;

-- report: revenue_per_quarter
SELECT strftime('%Y', o.order_date) || '-Q' || CAST(((CAST(strftime('%m', o.order_date) AS INTEGER) - 1) / 3 + 1) AS INTEGER) AS sales_quarter, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY sales_quarter ORDER BY sales_quarter;

-- report: revenue_per_year
SELECT strftime('%Y', o.order_date) AS sales_year, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY strftime('%Y', o.order_date) ORDER BY sales_year;

-- report: monthly_growth_rate
WITH monthly AS (SELECT strftime('%Y-%m', o.order_date) AS sales_month, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY strftime('%Y-%m', o.order_date)), comparison AS (SELECT sales_month, revenue, LAG(revenue) OVER (ORDER BY sales_month) AS previous_revenue FROM monthly)
SELECT sales_month, ROUND(revenue, 2) AS revenue, ROUND(100.0 * (revenue - previous_revenue) / NULLIF(previous_revenue, 0), 2) AS month_over_month_percent FROM comparison ORDER BY sales_month;

-- report: highest_revenue_month
SELECT strftime('%Y-%m', o.order_date) AS sales_month, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY sales_month ORDER BY revenue DESC LIMIT 1;

-- report: lowest_revenue_month
SELECT strftime('%Y-%m', o.order_date) AS sales_month, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY sales_month ORDER BY revenue ASC LIMIT 1;

-- report: return_rate_by_product
SELECT p.product_id, p.product_name, ROUND(100.0 * SUM(CASE WHEN o.status = 'RETURNED' THEN i.quantity ELSE 0 END) / NULLIF(SUM(i.quantity), 0), 2) AS return_rate_percent FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id GROUP BY p.product_id, p.product_name ORDER BY return_rate_percent DESC;

-- report: return_rate_by_category
SELECT p.category, ROUND(100.0 * SUM(CASE WHEN o.status = 'RETURNED' THEN i.quantity ELSE 0 END) / NULLIF(SUM(i.quantity), 0), 2) AS return_rate_percent FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id GROUP BY p.category ORDER BY return_rate_percent DESC;

-- report: return_rate_by_customer
SELECT c.customer_id, c.customer_name, ROUND(100.0 * SUM(CASE WHEN o.status = 'RETURNED' THEN i.quantity ELSE 0 END) / NULLIF(SUM(i.quantity), 0), 2) AS return_rate_percent FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name ORDER BY return_rate_percent DESC;

-- report: top_returned_categories
SELECT p.category, SUM(CASE WHEN o.status = 'RETURNED' THEN i.quantity ELSE 0 END) AS returned_units FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id GROUP BY p.category ORDER BY returned_units DESC LIMIT 10;

-- report: high_value_orders_above_average
SELECT o.order_id, o.customer_id, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS order_value FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY o.order_id, o.customer_id HAVING SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) > (SELECT AVG(order_value) FROM (SELECT SUM(quantity * unit_price * (1 - discount_percent / 100.0)) AS order_value FROM order_items GROUP BY order_id)) ORDER BY order_value DESC;

-- report: customers_above_average_lifetime_value
SELECT c.customer_id, c.customer_name, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS lifetime_value FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name HAVING SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) > (SELECT AVG(customer_value) FROM (SELECT SUM(i2.quantity * i2.unit_price * (1 - i2.discount_percent / 100.0)) AS customer_value FROM orders o2 JOIN order_items i2 ON i2.order_id = o2.order_id WHERE o2.customer_id IS NOT NULL GROUP BY o2.customer_id)) ORDER BY lifetime_value DESC;

-- report: products_above_category_average_price
SELECT p.product_id, p.product_name, p.category, p.selling_price FROM products p WHERE p.selling_price > (SELECT AVG(p2.selling_price) FROM products p2 WHERE p2.category = p.category) ORDER BY p.category, p.selling_price DESC;

-- report: customer_tier_distribution
SELECT CASE WHEN lifetime_value >= 50000 THEN 'HIGH_VALUE' WHEN lifetime_value >= 20000 THEN 'MID_VALUE' ELSE 'STANDARD' END AS customer_tier, COUNT(*) AS customers FROM (SELECT c.customer_id, COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0) AS lifetime_value FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id) GROUP BY customer_tier ORDER BY customers DESC;
