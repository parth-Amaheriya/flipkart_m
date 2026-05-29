from datetime import datetime
import json
import mysql.connector
from typing import Dict, List

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "flipkart_minutes_test"
}

LINK_LIMIT = 50

date = datetime.now().strftime("%Y_%m_%d")
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)
    
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Existing table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS pdp_data_{date} (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        locality VARCHAR(100),
        sku varchar(100) NOT NULL,
        url VARCHAR(500) NOT NULL,
        pincode VARCHAR(10) NOT NULL,
        city VARCHAR(100),
        state VARCHAR(100),
        product_name VARCHAR(500),
        brand VARCHAR(200),
        stock_avaliblity_status VARCHAR(10) DEFAULT 'NO',
        EAN_code VARCHAR(50),
        pls JSON,
        product_data JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_sku_pincode (sku, pincode)
    );
    """)

    # NEW TABLE: Deliverable Pincodes
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS final_pincode_deliverable_{date} (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        pincode VARCHAR(10) NOT NULL UNIQUE,
        ud VARCHAR(5000) NOT NULL,
        latitude DECIMAL(10, 6),
        longitude DECIMAL(10, 6),
        city VARCHAR(100),
        state VARCHAR(100),
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

def create_master_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SHOW TABLES LIKE 'master_product_pincode_{date}'")

    if cursor.fetchone():
        print("master_product_pincode table already exists.")
        return

    cursor.execute(f"""
    CREATE TABLE master_product_pincode_{date} (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    ean_code VARCHAR(50),
    product_url TEXT,

    pincode INT,
    ud varchar(5000),

    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),

    city VARCHAR(100),
    state VARCHAR(100),
    locality VARCHAR(255),
    location VARCHAR(100),

    status VARCHAR(20) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_product_pincode (product_url(255), pincode)
);""")

    cursor.execute(f"""
INSERT INTO master_product_pincode_{date} (
    ean_code,
    product_url,
    pincode,
    ud,
    latitude,
    longitude,
    city,
    state,
    locality,
    location,
    status
)
SELECT DISTINCT
    CASE
        WHEN p.ean_code IS NULL
             OR TRIM(p.ean_code) = ''
             OR LOWER(TRIM(p.ean_code)) = 'nan'
        THEN 'N/A'
        ELSE TRIM(p.ean_code)
    END AS ean_code,
    
    p.url,
    pc.pincode,
    pc.ud,
    pc.latitude,
    pc.longitude,
    pc.city,
    pc.state,
    pc.locality,
    pc.location,
    'pending'
FROM products_urls p
CROSS JOIN final_pincode_deliverable_{date} pc;
""")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Master table created and updated successfully.")

def get_unique_pending_pincodes(limit: int = LINK_LIMIT) -> List[Dict]:
    """Fetch pending pincodes with their row ids for status updates"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"""
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


def insert_deliverable_pincode(pincode: str, ud: str, lat: float, lng: float, city: str, locality: str, location: str, state: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"""
            INSERT INTO final_pincode_deliverable_{date}
            (pincode,ud, latitude, longitude, city, locality, location, state, is_deliverable)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON DUPLICATE KEY UPDATE 
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                city = VALUES(city),
                locality = VALUES(locality),
                location = VALUES(location),
                state = VALUES(state),
                checked_at = CURRENT_TIMESTAMP
        """, (pincode, ud, lat, lng, city, locality, location, state))
        conn.commit()
    except Exception as e:
        print(f"❌ Error inserting deliverable pincode {pincode}: {e}")
    finally:
        cursor.close()
        conn.close()


# def get_deliverable_pincodes(limit: int = LINK_LIMIT) -> List[Dict]:
#     """Get deliverable pincodes for product scraping"""
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute(f"""
#         SELECT *
#         FROM master_product_pincode_{date}
#         WHERE status = 'pending'
#         LIMIT %s
#     """, (limit,))

#     rows = cursor.fetchall()

#     if rows:
#         ids = [row['id'] for row in rows]
#         placeholders = ','.join(['%s'] * len(ids))
#         cursor.execute(f"""
#             UPDATE master_product_pincode_{date}
#             SET status = 'processing'
#             WHERE id IN ({placeholders})
#         """, ids)
#         conn.commit()

#     cursor.close()
#     conn.close()
#     return rows
def get_deliverable_pincodes_for_product(product_title: str, city: str, limit: int = LINK_LIMIT) -> List[Dict]:
    """Get deliverable pincodes for a specific product + city combination"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"""
        SELECT m.*
        FROM master_product_pincode_{date} m
        JOIN products_urls p ON m.product_url = p.url
        WHERE m.status = 'pending'
          AND p.product_title = %s
          AND p.city = %s
        LIMIT %s
    """, (product_title, city, limit))

    rows = cursor.fetchall()

    if rows:
        ids = [row['id'] for row in rows]
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"""
            UPDATE master_product_pincode_{date}
            SET status = 'processing'
            WHERE id IN ({placeholders})
        """, ids)
        conn.commit()

    cursor.close()
    conn.close()
    return rows


def update_status_pincode(table,record_id: int, status: str = "done"):
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

def update_status(table,record_id: int, status: str = "done"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {table}_{date}
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
        query = f"""
    INSERT IGNORE INTO pdp_data_{date} 
    (
        sku,
        url,
        pincode,
        locality,
        city,
        state,
        product_name,
        brand,
        stock_avaliblity_status,
        EAN_code,
        pls,
        product_data
    )
    VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

        cursor.execute(query, (
            product_dict.get('sku'),
            product_dict.get('url'),
            product_dict.get('pincode'),
            product_dict.get('locality'),
            product_dict.get('city'),
            product_dict.get('state'),
            product_dict.get('product_name'),
            product_dict.get('brand'),
            product_dict.get('stock_avaliblity_status'),
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