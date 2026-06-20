import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not API_KEY:
    raise ValueError("Missing GOOGLE_PLACES_API_KEY in .env file")

URL = "https://places.googleapis.com/v1/places:searchText"

NEIGHBOURHOODS = [
    "Downtown Vancouver",
    "Yaletown",
    "Gastown",
    "Kitsilano",
    "Mount Pleasant",
    "Commercial Drive",
    "West End",
    "Richmond",
    "Burnaby",
    "North Vancouver"
]

CUISINES = [
    "Japanese",
    "Chinese",
    "Indian",
    "Italian",
    "Mexican",
    "Korean",
    "Thai",
    "Vietnamese",
    "Mediterranean",
    "Seafood",
    "Peruvian",
    "French",
    "Spanish",
    "Lebanese",
    "Turkish",
    "Ethiopian",
    "Brazilian",
    "Caribbean",
    "Vegetarian",
    "Vegan",
]

QUERIES = []

for neighbourhood in NEIGHBOURHOODS:
    for cuisine in CUISINES:
        QUERIES.append(
            f"{cuisine} restaurants in {neighbourhood} BC"
        )

HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": (
        "places.id,"
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.rating,"
        "places.userRatingCount,"
        "places.priceLevel,"
        "places.primaryType,"
        "places.types,"
        "places.websiteUri,"
        "places.googleMapsUri"
    ),
}


def fetch_places(query):
    places = []
    page_token = None

    while True:
        body = {
            "textQuery": query,
            "regionCode": "CA",
            "languageCode": "en",
            "maxResultCount": 20,
        }

        if page_token:
            body["pageToken"] = page_token
            time.sleep(2)

        response = requests.post(URL, headers=HEADERS, json=body)
        response.raise_for_status()

        data = response.json()
        places.extend(data.get("places", []))

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return places


def flatten_place(place, search_query):
    location = place.get("location", {})
    display_name = place.get("displayName", {})

    return {
        "place_id": place.get("id"),
        "name": display_name.get("text"),
        "address": place.get("formattedAddress"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "rating": place.get("rating"),
        "review_count": place.get("userRatingCount"),
        "price_level": place.get("priceLevel"),
        "primary_type": place.get("primaryType"),
        "types": ", ".join(place.get("types", [])),
        "website": place.get("websiteUri"),
        "google_maps_url": place.get("googleMapsUri"),
        "search_query": search_query,
    }


def main():
    all_places = []

    for query in QUERIES:
        print(f"Fetching: {query}")
        results = fetch_places(query)

        for place in results:
            all_places.append(flatten_place(place, query))

    df = pd.DataFrame(all_places)

    df = df.drop_duplicates(subset=["place_id"])
    df = df.sort_values(by=["rating", "review_count"], ascending=False)

    output_path = "data/raw/google_places_vancouver.csv"
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} restaurants to {output_path}")


if __name__ == "__main__":
    main()