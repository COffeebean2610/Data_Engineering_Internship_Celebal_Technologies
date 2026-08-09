-- SQLite applies primary-key, UNIQUE, CHECK, NOT NULL, and foreign-key rules
-- declared in schema.sql. These triggers add date-quality protection that SQLite
-- CHECK constraints cannot express reliably for text dates.
CREATE TRIGGER IF NOT EXISTS trg_orders_order_date_format_insert
BEFORE INSERT ON orders
WHEN datetime(NEW.order_date) IS NULL
BEGIN
    SELECT RAISE(ABORT, 'orders.order_date must be a valid ISO-8601 date');
END;

CREATE TRIGGER IF NOT EXISTS trg_orders_order_date_format_update
BEFORE UPDATE OF order_date ON orders
WHEN datetime(NEW.order_date) IS NULL
BEGIN
    SELECT RAISE(ABORT, 'orders.order_date must be a valid ISO-8601 date');
END;
