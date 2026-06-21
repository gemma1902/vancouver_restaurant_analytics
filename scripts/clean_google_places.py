import pandas as pd

df = pd.read_csv("data/raw/google_places_vancouver.csv")

print("Rows before:", len(df))

# Remove duplicates
df = df.drop_duplicates(subset=["place_id"])

# Remove rows without names
df = df.dropna(subset=["name"])

# Remove rows without ratings
df = df.dropna(subset=["rating"])

# Fill missing review counts
df["review_count"] = df["review_count"].fillna(0)

# Convert types
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce")

# Remove low quality entries
df = df[df["review_count"] >= 5]

print("Rows after:", len(df))

df.to_csv(
    "data/processed/google_places_clean.csv",
    index=False
)

print("Clean dataset saved")