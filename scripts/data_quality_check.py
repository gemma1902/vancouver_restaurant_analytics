import pandas as pd

df = pd.read_csv("data/raw/google_places_vancouver.csv")

print("\n========== DATA QUALITY REPORT ==========\n")

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\n--- Columns ---")
print(df.columns.tolist())

print("\n--- Missing Values ---")
print(df.isnull().sum().sort_values(ascending=False))

print("\n--- Duplicate Place IDs ---")
print(df.duplicated(subset=["place_id"]).sum())

print("\n--- Duplicate Restaurant Names ---")
print(df.duplicated(subset=["name"]).sum())

print("\n--- Rating Statistics ---")
print(df["rating"].describe())

print("\n--- Review Count Statistics ---")
print(df["review_count"].describe())

print("\n--- Top 20 Most Common Types ---")
print(df["primary_type"].value_counts().head(20))

print("\n--- Rows Missing Ratings ---")
print(df["rating"].isna().sum())

print("\n--- Rows Missing Review Count ---")
print(df["review_count"].isna().sum())

print("\n--- Top 10 Highest Rated Restaurants ---")
print(
    df.sort_values(
        ["rating", "review_count"],
        ascending=False
    )[["name", "rating", "review_count"]].head(10)
)

print(sorted(df["primary_type"].dropna().unique()))

remove_types = [
    "asian_grocery_store",
    "grocery_store",
    "food_store",
    "market",
    "manufacturer",
    "massage",
    "spa",
    "place_of_worship",
    "service",
    "live_music_venue"
]

print(
    df[df["primary_type"].isin(remove_types)]
    ["primary_type"]
    .value_counts()
)

df = df[~df["primary_type"].isin(remove_types)]

couprice_map = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4
}

df["price_numeric"] = df["price_level"].map(couprice_map)

# Count how many of each price level per primary_type
price_counts = (
    df.groupby(["primary_type", "price_level"])
    .size()
    .reset_index(name="count")
    .sort_values(["primary_type", "count"], ascending=[True, False])
)

print(price_counts)

# Average price level per primary_type
avg_price_by_type = (
    df.groupby("primary_type")["price_numeric"]
    .mean()
    .round()
)

print(avg_price_by_type)

# Overall average price level fallback
overall_avg_price = round(df["price_numeric"].mean())

# Impute missing price_numeric using average for that primary_type
df["price_numeric_imputed"] = df["price_numeric"]

df["price_numeric_imputed"] = df.apply(
    lambda row: avg_price_by_type[row["primary_type"]]
    if pd.isna(row["price_numeric_imputed"]) and row["primary_type"] in avg_price_by_type.index
    else row["price_numeric_imputed"],
    axis=1
)

# If any are still missing, use overall average
df["price_numeric_imputed"] = df["price_numeric_imputed"].fillna(overall_avg_price)

# Convert back to labels/symbols
price_symbol_map = {
    0: "Free",
    1: "$",
    2: "$$",
    3: "$$$",
    4: "$$$$"
}

df["price_tier_imputed"] = (
    df["price_numeric_imputed"]
    .astype(int)
    .map(price_symbol_map)
)

print(df[["name", "primary_type", "price_level", "price_numeric_imputed", "price_tier_imputed"]].head(20))

print(df["price_tier_imputed"].isna().sum())
print(round(df["price_tier_imputed"].isna().mean() * 100, 2), "% missing")
df = df.drop(columns=["price_level"])
df = df.drop(columns=["price_numeric"])    
df = df.dropna(
    subset=[
        "rating",
        "review_count",
        "primary_type"
    ]
)

price_tier_map = {
    "$": 1,
    "$$": 2,
    "$$$": 3,
    "$$$$": 4
}

df["price_tier_numeric"] = (
    df["price_tier_imputed"]
    .map(price_tier_map)
)
print("\n--- Missing Values ---")
print(df.isnull().sum().sort_values(ascending=False))

df.to_csv(
    "data/processed/google_places_clean.csv",
    index=False
)