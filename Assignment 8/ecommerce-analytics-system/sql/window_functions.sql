-- report: customer_lifetime_value_ranks
WITH customer_value AS (SELECT c.customer_id, c.customer_name, COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0) AS lifetime_value FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name)
SELECT customer_id, customer_name, ROUND(lifetime_value, 2) AS lifetime_value, RANK() OVER (ORDER BY lifetime_value DESC) AS value_rank, DENSE_RANK() OVER (ORDER BY lifetime_value DESC) AS dense_value_rank, ROW_NUMBER() OVER (ORDER BY lifetime_value DESC, customer_id) AS row_number FROM customer_value;

-- report: running_revenue_by_date
WITH daily_sales AS (SELECT date(o.order_date) AS sales_date, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS daily_revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY date(o.order_date))
SELECT sales_date, ROUND(daily_revenue, 2) AS daily_revenue, ROUND(SUM(daily_revenue) OVER (ORDER BY sales_date), 2) AS running_revenue FROM daily_sales ORDER BY sales_date;

-- report: seven_day_moving_average
WITH daily_sales AS (SELECT date(o.order_date) AS sales_date, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS daily_revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY date(o.order_date))
SELECT sales_date, ROUND(daily_revenue, 2) AS daily_revenue, ROUND(AVG(daily_revenue) OVER (ORDER BY sales_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS moving_average_7_day FROM daily_sales ORDER BY sales_date;

-- report: daily_cumulative_revenue
WITH daily_sales AS (SELECT date(o.order_date) AS sales_date, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS daily_revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY date(o.order_date))
SELECT sales_date, ROUND(SUM(daily_revenue) OVER (ORDER BY sales_date ROWS UNBOUNDED PRECEDING), 2) AS cumulative_revenue FROM daily_sales ORDER BY sales_date;

-- report: products_ranked_within_category
WITH product_sales AS (SELECT p.category, p.product_id, p.product_name, COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0) AS revenue FROM products p LEFT JOIN order_items i ON i.product_id = p.product_id GROUP BY p.category, p.product_id, p.product_name)
SELECT category, product_id, product_name, ROUND(revenue, 2) AS revenue, RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS category_rank FROM product_sales ORDER BY category, category_rank;

-- report: running_sales_by_category
WITH category_daily_sales AS (SELECT p.category, date(o.order_date) AS sales_date, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id GROUP BY p.category, date(o.order_date))
SELECT category, sales_date, ROUND(revenue, 2) AS daily_revenue, ROUND(SUM(revenue) OVER (PARTITION BY category ORDER BY sales_date), 2) AS running_category_revenue FROM category_daily_sales ORDER BY category, sales_date;

-- report: customer_order_lag
WITH customer_orders AS (SELECT customer_id, date(order_date) AS order_date, LAG(date(order_date)) OVER (PARTITION BY customer_id ORDER BY date(order_date), order_id) AS previous_order_date FROM orders WHERE customer_id IS NOT NULL)
SELECT customer_id, order_date, previous_order_date, CAST(julianday(order_date) - julianday(previous_order_date) AS INTEGER) AS days_gap FROM customer_orders ORDER BY customer_id, order_date;

-- report: customer_next_purchase
SELECT customer_id, date(order_date) AS order_date, LEAD(date(order_date)) OVER (PARTITION BY customer_id ORDER BY date(order_date), order_id) AS next_purchase_date FROM orders WHERE customer_id IS NOT NULL ORDER BY customer_id, order_date;

-- report: first_and_latest_purchased_category
WITH category_orders AS (SELECT o.customer_id, o.order_id, date(o.order_date) AS order_date, p.category FROM orders o JOIN order_items i ON i.order_id = o.order_id JOIN products p ON p.product_id = i.product_id WHERE o.customer_id IS NOT NULL GROUP BY o.customer_id, o.order_id, date(o.order_date), p.category), values_by_customer AS (SELECT customer_id, FIRST_VALUE(category) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS first_purchased_category, LAST_VALUE(category) OVER (PARTITION BY customer_id ORDER BY order_date, order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS latest_purchased_category, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC, order_id DESC) AS latest_row FROM category_orders)
SELECT customer_id, first_purchased_category, latest_purchased_category FROM values_by_customer WHERE latest_row = 1 ORDER BY customer_id;

-- report: customer_value_quartiles
WITH customer_value AS (SELECT c.customer_id, c.customer_name, COALESCE(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 0) AS lifetime_value FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id LEFT JOIN order_items i ON i.order_id = o.order_id GROUP BY c.customer_id, c.customer_name), quartiles AS (SELECT *, NTILE(4) OVER (ORDER BY lifetime_value DESC) AS value_quartile FROM customer_value)
SELECT customer_id, customer_name, ROUND(lifetime_value, 2) AS lifetime_value, CASE value_quartile WHEN 1 THEN 'Platinum' WHEN 2 THEN 'Gold' WHEN 3 THEN 'Silver' ELSE 'Bronze' END AS value_segment FROM quartiles ORDER BY lifetime_value DESC;
