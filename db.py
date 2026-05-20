import json
import mysql.connector
from typing import Dict, List

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "flipkart_minutes_final"
}

LINK_LIMIT = 50


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Existing table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pdp_data (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        locality VARCHAR(100),
        sku varchar(100) NOT NULL,
        url VARCHAR(500) NOT NULL,
        pincode VARCHAR(10) NOT NULL,
        city VARCHAR(100),
        product_name VARCHAR(500),
        brand VARCHAR(200),
        stock_availability_status VARCHAR(10) DEFAULT 'NO',
        EAN_code VARCHAR(50),
        pls JSON,
        product_data JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_sku_pincode (sku, pincode)
    );
    """)

    # NEW TABLE: Deliverable Pincodes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS final_pincode_deliverable (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        pincode VARCHAR(10) NOT NULL UNIQUE,
        latitude DECIMAL(10, 6),
        longitude DECIMAL(10, 6),
        city VARCHAR(100),
        locality VARCHAR(200),
        location VARCHAR(200),
        is_deliverable BOOLEAN DEFAULT TRUE,
        status VARCHAR(20) DEFAULT 'pending',
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_pincode (pincode)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tables verified/created successfully.")


def get_unique_pending_pincodes(limit: int = LINK_LIMIT) -> List[Dict]:
    """Fetch pending pincodes with their row ids for status updates"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT id, pincode, location
    FROM pincodes
    WHERE id IN (
        SELECT MIN(id)
        FROM pincodes
        WHERE status = 'pending'
        GROUP BY pincode
    )
    ORDER BY id
    LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()

    if rows:
        ids = [row['id'] for row in rows]
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"""
            UPDATE pincodes
            SET status = 'processing'
            WHERE id IN ({placeholders})
        """, ids)
        conn.commit()

    cursor.close()
    conn.close()
    return rows


def insert_deliverable_pincode(pincode: str, lat: float, lng: float, city: str, locality: str, location: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO final_pincode_deliverable
            (pincode, latitude, longitude, city, locality, location, is_deliverable)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            ON DUPLICATE KEY UPDATE 
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                city = VALUES(city),
                locality = VALUES(locality),
                location = VALUES(location),
                checked_at = CURRENT_TIMESTAMP
        """, (pincode, lat, lng, city, locality, location))
        conn.commit()
    except Exception as e:
        print(f"❌ Error inserting deliverable pincode {pincode}: {e}")
    finally:
        cursor.close()
        conn.close()


def get_deliverable_pincodes(limit: int = LINK_LIMIT) -> List[Dict]:
    """Get deliverable pincodes for product scraping"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM master_product_pincode 
        WHERE status = 'pending'
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()

    if rows:
        ids = [row['id'] for row in rows]
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"""
            UPDATE master_product_pincode
            SET status = 'processing'
            WHERE id IN ({placeholders})
        """, ids)
        conn.commit()

    cursor.close()
    conn.close()
    return rows


def update_status(table,record_id: int, status: str = "done"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {table} 
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
    INSERT INTO pdp_data 
    (
        sku,
        url,
        pincode,
        locality,
        city,
        product_name,
        brand,
        stock_availability_status,
        EAN_code,
        pls,
        product_data
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

        cursor.execute(query, (
            product_dict.get('sku'),
            product_dict.get('url'),
            product_dict.get('pincode'),
            product_dict.get('locality'),
            product_dict.get('city'),
            product_dict.get('product_name'),
            product_dict.get('brand'),
            product_dict.get('stock_availability_status'),
            product_dict.get('EAN_code'),
            json.dumps(product_dict.get('pls')),
            json.dumps(product_dict.get('product_data'))
        ))
        conn.commit()

    except Exception as e:
        print(f"❌ DB Insert Error: {e}")
    finally:
        cursor.close()
        conn.close()