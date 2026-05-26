

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
PRODUCT_FILE = "ex/Flipkart Product vise locations.xlsx"
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
# READ PINCODE FILE
# =========================

pincode_df = pd.read_excel(PINCODE_FILE, sheet_name='Flipkart Minutes')

pincode_df.columns = pincode_df.columns.str.strip()
print(pincode_df.head())
print("Pincode Columns:")
print(pincode_df.columns.tolist())

# =========================
# INSERT PINCODES
# =========================

insert_pincode_query = """
INSERT INTO pincodes (
    location,
    pincode,
    status
)
VALUES (%s, %s, %s)
"""

for _, row in pincode_df.iterrows():

    location = str(row["Location"]).strip()
    pincode = str(row["Pincode"]).strip()

    cursor.execute(
        insert_pincode_query,
        (location, pincode,'pending')
    )

conn.commit()

print("Pincode data inserted successfully.")

# =========================
# READ PRODUCT FILE
# =========================

product_df = pd.read_excel(PRODUCT_FILE)


product_df.columns = product_df.columns.str.strip()
print(product_df.head())
print("\nProduct Columns:")
print(product_df.columns.tolist())

# =========================
# READ MAPPING FILE
# =========================

mapping_df = pd.read_excel(MAPPING_FILE,skiprows=1,sheet_name="Flipkart Minutes and Grocery", dtype={"EAN Code": str})
# print(mapping_df['Unnamed: 1'])
mapping_df.columns = mapping_df.columns.str.strip()
print(mapping_df.head())
print("\nMapping Columns:")
print(mapping_df.columns.tolist())
print(mapping_df['Unnamed: 2'].head())
# # =========================
# # KEEP ONLY REQUIRED COLUMNS
# # =========================

mapping_df = mapping_df[
    ["EAN Code","Article Description", "Unnamed: 2"]
]
print(mapping_df.head())

# =========================
# RENAME COLUMNS
# =========================

mapping_df.rename(
    columns={
        "Article Description": "product_title",
        "Unnamed: 2": "url"
    },
    inplace=True
)

# =========================
# KEEP ONLY VALID URL ROWS
# =========================

mapping_df = mapping_df[
    mapping_df["url"].notna() &
    (mapping_df["url"].astype(str).str.strip() != "") &
    (mapping_df["url"].astype(str).str.upper() != "N/A")
]
print("*"*20)
print(len(mapping_df['url'].unique()))
print("\nFiltered Mapping Data:")
print(mapping_df.head())

# =========================
# KEEP REQUIRED COLUMNS ONLY
# =========================

mapping_df = mapping_df[
    ["EAN Code","product_title", "url"]
]

# =========================
# MERGE PRODUCT + URL
# =========================

merged_df = pd.merge(
    product_df,
    mapping_df,
    on="product_title",
    how="inner"   # only matched products with URL
)

print("\nMerged Data:")
print(merged_df.head())

# =========================
# INSERT PRODUCTS
# =========================

insert_product_query = """
INSERT INTO products_urls (
        EAN_Code,
        city,
        product_title,
        url
)
VALUES (%s, %s, %s, %s)
"""

for _, row in merged_df.iterrows():

    ean_code = str(row["EAN Code"]).strip()
    city = str(row["City"]).strip()
    product_title = str(row["product_title"]).strip()
    url = str(row["url"]).strip()

    cursor.execute(
        insert_product_query,
        (
            ean_code,
            city,
            product_title,
            url
        )
    )

conn.commit()

print("Product data inserted successfully.")
