SELECT * FROM flipkart_minutes_final.products_urls;
SELECT * FROM flipkart_minutes_final.final_pincode_deliverable;
-- CREATE TABLE flipkart_minutes_final.master_product_pincode (
--     id BIGINT AUTO_INCREMENT PRIMARY KEY,
--     ean_code BIGINT,
--     description VARCHAR(255),
--     product_url TEXT,

--     pincode INT,
--     latitude DECIMAL(10,6),
--     longitude DECIMAL(10,6),
--     city VARCHAR(100),
--     locality VARCHAR(255),
--     location VARCHAR(100),

--     status VARCHAR(20) DEFAULT 'pending',

--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
use flipkart_minutes_final;
INSERT INTO master_product_pincode (
    ean_code,
    description,
    product_url,
    pincode,
    latitude,
    longitude,
    city,
    locality,
    location,
    status
)
SELECT 
    p.ean_code,
    p.description,
    p.url,
    pc.pincode,
    pc.latitude,
    pc.longitude,
    pc.city,
    pc.locality,
    pc.location,
    'pending'
FROM products_urls p
CROSS JOIN final_pincode_deliverable pc;