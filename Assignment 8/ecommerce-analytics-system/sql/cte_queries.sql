-- report: cte_monthly_revenue
WITH monthly_sales AS (SELECT strftime('%Y-%m', o.order_date) AS sales_month, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY strftime('%Y-%m', o.order_date)) SELECT sales_month, ROUND(revenue, 2) AS revenue FROM monthly_sales ORDER BY sales_month;

-- report: cte_monthly_growth_rate
WITH monthly_sales AS (SELECT strftime('%Y-%m', o.order_date) AS sales_month, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY strftime('%Y-%m', o.order_date)), prior_month AS (SELECT sales_month, revenue, LAG(revenue) OVER (ORDER BY sales_month) AS previous_revenue FROM monthly_sales) SELECT sales_month, ROUND(revenue, 2) AS revenue, ROUND(100.0 * (revenue - previous_revenue) / NULLIF(previous_revenue, 0), 2) AS growth_percent FROM prior_month ORDER BY sales_month;

-- report: cte_revenue_by_customer
WITH line_revenue AS (SELECT o.customer_id, i.quantity * i.unit_price * (1 - i.discount_percent / 100.0) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id), customer_revenue AS (SELECT customer_id, SUM(revenue) AS revenue FROM line_revenue GROUP BY customer_id) SELECT c.customer_id, c.customer_name, ROUND(COALESCE(cr.revenue, 0), 2) AS revenue FROM customers c LEFT JOIN customer_revenue cr ON cr.customer_id = c.customer_id ORDER BY revenue DESC;

-- report: cte_revenue_by_category
WITH line_revenue AS (SELECT i.product_id, i.quantity * i.unit_price * (1 - i.discount_percent / 100.0) AS revenue FROM order_items i), category_revenue AS (SELECT p.category, SUM(l.revenue) AS revenue FROM products p JOIN line_revenue l ON l.product_id = p.product_id GROUP BY p.category) SELECT category, ROUND(revenue, 2) AS revenue FROM category_revenue ORDER BY revenue DESC;

-- report: cte_top_customers_every_month
WITH monthly_customer_revenue AS (SELECT strftime('%Y-%m', o.order_date) AS sales_month, c.customer_id, c.customer_name, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id GROUP BY sales_month, c.customer_id, c.customer_name), ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY sales_month ORDER BY revenue DESC) AS monthly_rank FROM monthly_customer_revenue) SELECT sales_month, customer_id, customer_name, ROUND(revenue, 2) AS revenue FROM ranked WHERE monthly_rank <= 10 ORDER BY sales_month, revenue DESC;

-- report: cte_top_products_every_month
WITH monthly_product_revenue AS (SELECT strftime('%Y-%m', o.order_date) AS sales_month, p.product_id, p.product_name, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id JOIN orders o ON o.order_id = i.order_id GROUP BY sales_month, p.product_id, p.product_name), ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY sales_month ORDER BY revenue DESC) AS monthly_rank FROM monthly_product_revenue) SELECT sales_month, product_id, product_name, ROUND(revenue, 2) AS revenue FROM ranked WHERE monthly_rank <= 10 ORDER BY sales_month, revenue DESC;

-- report: cte_customer_lifetime_value
WITH order_values AS (SELECT o.customer_id, o.order_id, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS order_value FROM orders o JOIN order_items i ON i.order_id = o.order_id WHERE o.customer_id IS NOT NULL GROUP BY o.customer_id, o.order_id), customer_value AS (SELECT customer_id, COUNT(*) AS order_count, SUM(order_value) AS lifetime_value FROM order_values GROUP BY customer_id) SELECT c.customer_id, c.customer_name, cv.order_count, ROUND(cv.lifetime_value, 2) AS lifetime_value FROM customer_value cv JOIN customers c ON c.customer_id = cv.customer_id ORDER BY lifetime_value DESC;

-- report: cte_product_lifetime_revenue
WITH product_lines AS (SELECT product_id, quantity, quantity * unit_price * (1 - discount_percent / 100.0) AS revenue FROM order_items), product_lifetime AS (SELECT product_id, SUM(quantity) AS units_sold, SUM(revenue) AS lifetime_revenue FROM product_lines GROUP BY product_id) SELECT p.product_id, p.product_name, pl.units_sold, ROUND(pl.lifetime_revenue, 2) AS lifetime_revenue FROM product_lifetime pl JOIN products p ON p.product_id = pl.product_id ORDER BY lifetime_revenue DESC;

-- report: cte_repeat_customer_analysis
WITH customer_orders AS (SELECT customer_id, COUNT(*) AS order_count FROM orders WHERE customer_id IS NOT NULL GROUP BY customer_id), segments AS (SELECT CASE WHEN order_count = 1 THEN 'One-Time' ELSE 'Repeat' END AS customer_type FROM customer_orders) SELECT customer_type, COUNT(*) AS customers, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_percent FROM segments GROUP BY customer_type;

-- report: cte_churn_analysis
WITH latest_purchase AS (SELECT customer_id, MAX(date(order_date)) AS latest_order_date FROM orders WHERE customer_id IS NOT NULL GROUP BY customer_id), customer_status AS (SELECT c.customer_id, CASE WHEN lp.latest_order_date IS NULL OR lp.latest_order_date < date('now', '-90 days') THEN 'Churned' ELSE 'Active' END AS churn_status FROM customers c LEFT JOIN latest_purchase lp ON lp.customer_id = c.customer_id) SELECT churn_status, COUNT(*) AS customers, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_percent FROM customer_status GROUP BY churn_status;
