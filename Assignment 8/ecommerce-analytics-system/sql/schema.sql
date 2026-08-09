-- Core E-Commerce schema. Run this file first when deploying the database.
-- TEXT is used for stable business identifiers and ISO-8601 date values.
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    registration_date TEXT,
    customer_type TEXT NOT NULL CHECK (customer_type IN ('REGULAR', 'PREMIUM', 'VIP'))
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    cost_price REAL NOT NULL CHECK (cost_price >= 0),
    selling_price REAL NOT NULL CHECK (selling_price >= 0),
    stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
    profit_margin REAL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PLACED', 'SHIPPED', 'DELIVERED', 'RETURNED', 'CANCELLED')),
    region_code TEXT,
    payment_method TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_percent REAL NOT NULL CHECK (discount_percent BETWEEN 0 AND 100),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);
