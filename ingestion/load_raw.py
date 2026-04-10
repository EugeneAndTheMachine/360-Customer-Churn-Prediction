import pandas as pd 
from sqlalchemy import create_engine
from db_config import DB_URL

CSV_FILES = {
    "olist_customers_dataset.csv" : "raw_customers",
    "olist_orders_dataset.csv" : "raw_orders",
    "olist_order_items_dataset.csv" : "raw_order_items",
    "olist_order_payments_dataset.csv" : "raw_order_payments",
    "olist_order_reviews_dataset.csv" : "raw_order_reviews",
    "olist_products_dataset.csv" : "raw_products",
    "olist_sellers_dataset.csv" : "raw_sellers",
    "olist_geolocation_dataset.csv" : "raw_geolocation",
    "product_category_name_translation.csv" : "raw_product_category_name_translation"
}

DATA_DIR = "../data"

def load_csv():
    engine = create_engine(DB_URL)
    for filename, table_name in CSV_FILES.items():
        path = f"{DATA_DIR}/{filename}"
        print(f"Loading {filename} -> {table_name} ...")
        df = pd.read_csv(path)
        df.to_sql(
            name=table_name,
            con=engine,
            schema="public",
            if_exists="replace", # replace if exists for a new running
            index=False,
            chunksize=1000 # timeout avoidance
        )
        print(f"  Done: {len(df):,} rows")
    print("\nAll tables loaded successfully.")

if __name__ == "__main__":
    load_csv()