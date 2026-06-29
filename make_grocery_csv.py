#!/usr/bin/env python3
"""
Optional helper script.

This creates grocery_stores.csv using the same City of Chicago Food Inspections
source/filter/dedupe logic from the original build_map.py.

The GitHub Pages site does not require this file to run. The browser version in
index.html fetches the same data directly from the City of Chicago API.
"""

import math
from pathlib import Path

import pandas as pd
import requests

SOCRATA_URL = "https://data.cityofchicago.org/resource/4ijn-s7e5.json"
SOURCE_NAME = "City of Chicago Food Inspections"

WHERE_CLAUSE = (
    "latitude IS NOT NULL AND longitude IS NOT NULL AND ("
    "lower(facility_type) like '%grocery%' OR "
    "lower(facility_type) like '%convenience%' OR "
    "lower(facility_type) like '%supermarket%')"
)

SELECT_CLAUSE = "dba_name,facility_type,latitude,longitude"
DEDUP_DISTANCE_METERS = 35
ORIGINAL_TESTING_LIMIT = 75


def clean_name(name):
    if not name:
        return "Unnamed grocery store"
    return " ".join(str(name).strip().split())


def haversine_distance_meters(lat1, lon1, lat2, lon2):
    radius_earth_m = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth_m * c


def dedupe_stores(stores, distance_threshold_meters=DEDUP_DISTANCE_METERS):
    unique_stores = []

    for store in stores:
        duplicate_found = False

        for existing in unique_stores:
            same_name = store["name"].lower() == existing["name"].lower()
            distance = haversine_distance_meters(
                store["lat"], store["lon"], existing["lat"], existing["lon"]
            )

            if same_name and distance <= distance_threshold_meters:
                duplicate_found = True
                break

        if not duplicate_found:
            unique_stores.append(store)

    unique_stores.sort(key=lambda item: item["name"].lower())

    for index, store in enumerate(unique_stores, start=1):
        store["store_id"] = f"store_{index:04d}"

    return unique_stores


def fetch_city_rows():
    params = {
        "$limit": 50000,
        "$where": WHERE_CLAUSE,
        "$select": SELECT_CLAUSE,
    }

    response = requests.get(SOCRATA_URL, params=params, timeout=120)
    response.raise_for_status()
    return response.json()


def main():
    rows = fetch_city_rows()
    raw_stores = []

    for row in rows:
        try:
            lat = float(row.get("latitude"))
            lon = float(row.get("longitude"))
        except (TypeError, ValueError):
            continue

        raw_stores.append(
            {
                "name": clean_name(row.get("dba_name") or row.get("facility_type") or "Unnamed grocery store"),
                "facility_type": row.get("facility_type") or "",
                "lat": lat,
                "lon": lon,
                "source": SOURCE_NAME,
            }
        )

    stores = dedupe_stores(raw_stores)
    df = pd.DataFrame(stores, columns=["store_id", "name", "facility_type", "lat", "lon", "source"])

    full_path = Path("grocery_stores.csv")
    original_75_path = Path("grocery_stores_original_75.csv")

    df.to_csv(full_path, index=False)
    df.head(ORIGINAL_TESTING_LIMIT).to_csv(original_75_path, index=False)

    print(f"Raw rows from City of Chicago: {len(rows)}")
    print(f"Deduped stores: {len(df)}")
    print(f"Wrote {full_path}")
    print(f"Wrote {original_75_path}")


if __name__ == "__main__":
    main()
