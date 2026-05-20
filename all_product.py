from datetime import datetime
import pandas as pd
import pymysql


def adjust_time():
    """Adjust time for file naming convention."""
    now = datetime.now()
    return now.strftime("%Y_%m_%d")


todayDateTime = adjust_time()
scrape_date = datetime.now().strftime("%Y-%m-%d")

# todayDateTime = "2025_04_06"

con = pymysql.connect(
   host="localhost",
        user="root",
        password="actowiz",
        database="flipkart_minutes_final"
)

# create cursor, used to execute commands
qr = f"""select id,
        pincode,
        city,
        locality,
        sku,
        ean_code,
        url,
        product_name,
        brand,
        stock_avaliblity_status
    from pdp_data"""
df = pd.read_sql(qr, con)

# Drop column by name
# df.drop(columns=['id'], inplace=True)   # Replace 'column_name' with actual column name

# Add new columns
# df['platform'] = "Flipkart Minutes"
df['Scrape_date'] = scrape_date

# Instead, do this to control position:

# Insert at the beginning (position 0)
df.insert(9, 'platform', "Flipkart Minutes")
# Add serial number column
# df.insert(0, 'id', range(1, 1 + len(df)))

writer = pd.ExcelWriter(
    rf"flipkart_minutes_{todayDateTime}.xlsx",
    engine='xlsxwriter',
    engine_kwargs={"options": {'strings_to_urls': False}}
)

df.to_excel(writer, sheet_name='data', index=False)

# Access the workbook and worksheet objects
workbook = writer.book
worksheet = writer.sheets['data']

# Define a format with borders
border_format = workbook.add_format({'border': 1})  # Applies a thin border to all sides

# Get the range of the data
num_rows, num_cols = df.shape

worksheet.conditional_format(
    0, 0, num_rows, num_cols - 1,
    {'type': 'no_blanks', 'format': border_format}
)

worksheet.conditional_format(
    0, 0, num_rows, num_cols - 1,
    {'type': 'blanks', 'format': border_format}
)

writer.close()

