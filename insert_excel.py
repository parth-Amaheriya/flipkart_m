import pandas as pd
import mysql.connector

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "flipkart_minutes_final2"
}

# =========================
# FILE PATHS
# =========================
PINCODE_FILE = "ex/act-jnssav-7544-pincodes (1).xlsx"
PRODUCT_CITY_FILE = "ex/Flipkart Product vise locations.xlsx"   # ← Your main product-city table
MAPPING_FILE = "ex/Mapping Sheet.xlsx"

# =========================
# MYSQL CONNECTION
# =========================
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# =========================
# CREATE TABLES
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS pincodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(255),
    pincode VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products_urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    EAN_Code VARCHAR(50),
    city VARCHAR(255),
    product_title VARCHAR(500),
    url TEXT
)
""")

# =========================
# 1. INSERT PINCODES
# =========================
pincode_df = pd.read_excel(PINCODE_FILE, sheet_name='Flipkart Minutes')
pincode_df.columns = pincode_df.columns.str.strip()

insert_pincode_query = """
INSERT INTO pincodes (location, pincode, status)
VALUES (%s, %s, %s)
"""

for _, row in pincode_df.iterrows():
    location = str(row["Location"]).strip()
    pincode = str(row["Pincode"]).strip()
    cursor.execute(insert_pincode_query, (location, pincode, 'pending'))

conn.commit()
print("✅ Pincodes inserted successfully.")

# =========================
# 2. READ PRODUCT → CITY MAPPING (Your main table)
# =========================
product_city_df = pd.read_excel(PRODUCT_CITY_FILE)
product_city_df.columns = product_city_df.columns.str.strip()

print("Product-City Columns:", product_city_df.columns.tolist())

# =========================
# 3. READ URL MAPPING
# =========================
mapping_df = pd.read_excel(MAPPING_FILE, skiprows=1, sheet_name="Flipkart Minutes and Grocery", dtype={"EAN Code": str})
mapping_df.columns = mapping_df.columns.str.strip()

mapping_df = mapping_df[["EAN Code", "Article Description", "Unnamed: 2"]]
mapping_df.rename(columns={
    "Article Description": "product_title",
    "Unnamed: 2": "url"
}, inplace=True)

# Clean URLs
mapping_df = mapping_df[
    mapping_df["url"].notna() &
    (mapping_df["url"].astype(str).str.strip() != "") &
    (mapping_df["url"].astype(str).str.upper() != "N/A")
]

# =========================
# 4. MERGE: Product-City + URL Mapping
# =========================
merged_df = pd.merge(
    product_city_df,
    mapping_df,
    on="product_title",
    how="inner"
)

print(f"✅ Merged {len(merged_df)} product-city-url records")

# =========================
# 5. INSERT INTO products_urls
# =========================
insert_product_query = """
INSERT INTO products_urls (EAN_Code, city, product_title, url)
VALUES (%s, %s, %s, %s)
"""

for _, row in merged_df.iterrows():
    ean_code = str(row["EAN Code"]).strip()
    city = str(row["City"]).strip()
    product_title = str(row["product_title"]).strip()
    url = str(row["url"]).strip()

    cursor.execute(insert_product_query, (ean_code, city, product_title, url))

conn.commit()
print("✅ Product → City → URL mapping inserted successfully.")