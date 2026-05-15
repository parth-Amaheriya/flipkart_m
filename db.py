import mysql.connector
from typing import Dict

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "FLIPKART_MINUTES_DB"
}

LINK_LIMIT = 20


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS product_data (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        sku varchar(100) NOT NULL,
        url VARCHAR(500) NOT NULL,
        pincode VARCHAR(10) NOT NULL,
        city VARCHAR(100),
        product_name VARCHAR(500),
        brand VARCHAR(200),
        stock_availability_status VARCHAR(10) DEFAULT 'NO',
        EAN_code VARCHAR(50),
        quantity VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        UNIQUE KEY unique_sku_pincode (sku, pincode)
    );
    """

    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Table 'product_data' verified/created successfully.")


def get_pending_urls_pincodes(limit: int = LINK_LIMIT):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, url, pincode 
        FROM product_urls_pincodes
        WHERE status = 'pending'
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()

    if rows:
        ids = [row['id'] for row in rows]
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"""
            UPDATE product_urls_pincodes 
            SET status = 'processing' 
            WHERE id IN ({placeholders})
        """, ids)
        conn.commit()

    cursor.close()
    conn.close()
    return rows


def update_status(record_id: int, status: str = "done"):
    """status can be: done, failed, not_serviceable"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE product_urls_pincodes 
        SET status = %s 
        WHERE id = %s
    """, (status, record_id))
    conn.commit()
    cursor.close()
    conn.close()


def insert_product_data(product_dict: Dict):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO product_data 
        (sku, url, pincode, city, product_name, brand, 
         stock_availability_status, EAN_code, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            city = VALUES(city),
            product_name = VALUES(product_name),
            brand = VALUES(brand),
            stock_availability_status = VALUES(stock_availability_status),
            EAN_code = VALUES(EAN_code),
            quantity = VALUES(quantity),
            updated_at = CURRENT_TIMESTAMP
        """

        cursor.execute(query, (
            product_dict.get('sku'),
            product_dict.get('url'),
            product_dict.get('pincode'),
            product_dict.get('city'),
            product_dict.get('product_name'),
            product_dict.get('brand'),
            product_dict.get('stock_avaliblity_status'),
            product_dict.get('EAN_code'),
            product_dict.get('quantity')
        ))
        conn.commit()

    except Exception as e:
        print(f"❌ DB Insert Error: {e}")
    finally:
        cursor.close()
        conn.close()