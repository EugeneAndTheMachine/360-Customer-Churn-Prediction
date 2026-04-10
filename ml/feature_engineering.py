import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL, FEATURE_COLS, ID_COLS, TARGET_COL

def load_data():
    """Load data from the database."""
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM mart_customer_360", engine)
    print(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
    return df
    
def prepare_features(df):
    """Prepare features for modeling."""
    # Only take numeric features + target
    cols = ID_COLS + FEATURE_COLS + [TARGET_COL]
    df = df[cols].copy()

    # Fill null
    df[FEATURE_COLS] = df[FEATURE_COLS].fillna(0)

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    ids = df[ID_COLS]

    print(f"Features: {X.shape[1]} cols")
    print(f"Target distribution:\n{y.value_counts()}")
    return X, y, ids

if __name__ == "__main__":
    df = load_data()
    X, y, ids = prepare_features(df)
    