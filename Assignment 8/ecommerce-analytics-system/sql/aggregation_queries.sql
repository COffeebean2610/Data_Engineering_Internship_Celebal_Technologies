-- Aggregate product, order, regional, and category analytics.
-- report: top_selling_products
SELECT p.product_id, p.product_name, SUM(i.quantity) AS units_sold FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.product_id, p.product_name ORDER BY units_sold DESC LIMIT 10;

-- report: lowest_selling_products
SELECT p.product_id, p.product_name, COALESCE(SUM(i.quantity), 0) AS units_sold FROM products p LEFT JOIN order_items i ON i.product_id = p.product_id GROUP BY p.product_id, p.product_name ORDER BY units_sold, p.product_name LIMIT 10;

-- report: top_revenue_products
SELECT p.product_id, p.product_name, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.product_id, p.product_name ORDER BY revenue DESC LIMIT 10;

-- report: products_highest_discount
SELECT p.product_id, p.product_name, ROUND(AVG(i.discount_percent), 2) AS average_discount_percent FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.product_id, p.product_name ORDER BY average_discount_percent DESC LIMIT 10;

-- report: products_maximum_returns
SELECT p.product_id, p.product_name, COALESCE(SUM(CASE WHEN o.status = 'RETURNED' THEN i.quantity ELSE 0 END), 0) AS returned_units FROM products p LEFT JOIN order_items i ON i.product_id = p.product_id LEFT JOIN orders o ON o.order_id = i.order_id GROUP BY p.product_id, p.product_name ORDER BY returned_units DESC LIMIT 10;

-- report: revenue_by_brand
SELECT COALESCE(p.brand, 'UNBRANDED') AS brand, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY COALESCE(p.brand, 'UNBRANDED') ORDER BY revenue DESC;

-- report: revenue_by_category
SELECT p.category, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.category ORDER BY revenue DESC;

-- report: revenue_by_subcategory
SELECT p.category, p.subcategory, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.category, p.subcategory ORDER BY revenue DESC;

-- report: daily_orders
SELECT date(order_date) AS order_day, COUNT(*) AS orders FROM orders GROUP BY date(order_date) ORDER BY order_day;

-- report: weekly_orders
SELECT strftime('%Y-W%W', order_date) AS order_week, COUNT(*) AS orders FROM orders GROUP BY strftime('%Y-W%W', order_date) ORDER BY order_week;

-- report: monthly_orders
SELECT strftime('%Y-%m', order_date) AS order_month, COUNT(*) AS orders FROM orders GROUP BY strftime('%Y-%m', order_date) ORDER BY order_month;

-- report: yearly_orders
SELECT strftime('%Y', order_date) AS order_year, COUNT(*) AS orders FROM orders GROUP BY strftime('%Y', order_date) ORDER BY order_year;

-- report: order_status_distribution
SELECT status, COUNT(*) AS orders, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS order_percent FROM orders GROUP BY status ORDER BY orders DESC;

-- report: orders_by_payment_method
SELECT COALESCE(payment_method, 'UNKNOWN') AS payment_method, COUNT(*) AS orders FROM orders GROUP BY COALESCE(payment_method, 'UNKNOWN') ORDER BY orders DESC;

-- report: revenue_by_status
SELECT o.status, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY o.status ORDER BY revenue DESC;

-- report: revenue_by_region
SELECT o.region_code, ROUND(SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)), 2) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY o.region_code ORDER BY revenue DESC;

-- report: average_order_value_by_region
WITH order_values AS (SELECT o.region_code, o.order_id, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS order_value FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY o.region_code, o.order_id)
SELECT region_code, ROUND(AVG(order_value), 2) AS average_order_value FROM order_values GROUP BY region_code ORDER BY average_order_value DESC;

-- report: units_sold_by_category
SELECT p.category, SUM(i.quantity) AS units_sold FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.category ORDER BY units_sold DESC;

-- report: category_contribution
WITH category_sales AS (SELECT p.category, SUM(i.quantity * i.unit_price * (1 - i.discount_percent / 100.0)) AS revenue FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.category)
SELECT category, ROUND(revenue, 2) AS revenue, ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS revenue_percent FROM category_sales ORDER BY revenue DESC;
