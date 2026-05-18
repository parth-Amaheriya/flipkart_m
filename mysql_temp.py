import pandas as pd
import mysql.connector

FILE_PATH = "act-jnssav-7544-sku-based-data-collection-from-q-commerce-platforms-weekly (1).xlsx"

df = pd.read_excel(
    FILE_PATH,
    sheet_name="Flipkart Minutes and Grocery",
    header=2
)

# Manually set correct column names
df.columns = [
    "EAN Code",
    "Article Description",
    "Flipkart Minutes URL",
    "Flipkart Grocery URL"
]

print(df.columns)

# Keep only valid Flipkart Minutes URLs
df = df[df["Flipkart Minutes URL"].notna()]
df = df[df["Flipkart Minutes URL"] != "N/A"]
df = df[df["Flipkart Minutes URL"] != ""]


def insert_products(df):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="actowiz",
        database="flipkart_minutes_final"
    )

    cursor = conn.cursor()
    create_table = """
CREATE TABLE IF NOT EXISTS products_urls (
    id INT AUTO_INCREMENT PRIMARY KEY,

    ean_code VARCHAR(50),

    description TEXT,

    url VARCHAR(300) UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
    cursor.execute(create_table)
    conn.commit()
    
    query = """
        INSERT INTO products_urls (
            ean_code,
            description,
            url
        )
        VALUES (%s, %s, %s)
    """

    data = [
        (
            str(row["EAN Code"]),
            row["Article Description"],
            row["Flipkart Minutes URL"]
        )
        for _, row in df.iterrows()
    ]

    cursor.executemany(query, data)
    conn.commit()

    print(f"Inserted {cursor.rowcount} rows")

    cursor.close()
    conn.close()


insert_products(df)