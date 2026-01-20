-- ==========================================
-- 1. DATABASE SETUP (Tables)
-- ==========================================

-- Create Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Create Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category_id INT REFERENCES categories(id) ON DELETE CASCADE,
    quantity INT DEFAULT 0 CHECK (quantity >= 0),
    price DECIMAL(10, 2) NOT NULL
);

-- ==========================================
-- 2. STORED FUNCTIONS (Logic)
-- ==========================================

-- Function 1: Get Total Stock (Mandatory Requirement)
CREATE OR REPLACE FUNCTION get_total_stock(cat_id INT)
RETURNS INT AS $$
DECLARE
    total INT;
BEGIN
    SELECT COALESCE(SUM(quantity), 0) INTO total
    FROM inventory
    WHERE category_id = cat_id;
    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- Function 2: Low Stock Alert (Extra Feature)
CREATE OR REPLACE FUNCTION get_low_stock(threshold INT)
RETURNS TABLE(id INT, product_name VARCHAR, quantity INT) AS $$
BEGIN
    RETURN QUERY
    SELECT i.id, i.product_name, i.quantity
    FROM inventory i
    WHERE i.quantity < threshold;
END;
$$ LANGUAGE plpgsql;

-- Function 3: Apply Discount (Extra Feature)
CREATE OR REPLACE FUNCTION apply_category_discount(cat_id INT, discount_percent DECIMAL)
RETURNS INT AS $$
DECLARE
    items_updated INT;
BEGIN
    UPDATE inventory
    SET price = price - (price * (discount_percent / 100.0))
    WHERE category_id = cat_id;
    
    GET DIAGNOSTICS items_updated = ROW_COUNT;
    RETURN items_updated;
END;
$$ LANGUAGE plpgsql;

-- Function 4: Remove Discount (Extra Feature)
CREATE OR REPLACE FUNCTION remove_category_discount(cat_id INT, discount_percent DECIMAL)
RETURNS INT AS $$
DECLARE
    items_updated INT;
BEGIN
    IF discount_percent >= 100 THEN
        RETURN 0;
    END IF;

    UPDATE inventory
    SET price = price / ((100 - discount_percent) / 100.0)
    WHERE category_id = cat_id;
    
    GET DIAGNOSTICS items_updated = ROW_COUNT;
    RETURN items_updated;
END;
$$ LANGUAGE plpgsql;