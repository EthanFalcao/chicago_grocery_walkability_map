# Chicago Grocery Store Walkability

This repo is set up for the simplest GitHub Pages deployment.

It uses **no API key**, **no Streamlit**, and **no GitHub Actions**.

## What to upload

Upload these files to the root of your repo:

```text
index.html
.nojekyll
README.md
make_grocery_csv.py
requirements.txt
```

GitHub Pages settings:

```text
Settings → Pages → Source: Deploy from a branch → main → / root → Save
```

Your site should be:

```text
https://ethanfalcao.github.io/chicago_grocery_walkability_map/
```

## Data source

This uses the same grocery data source/filter from the original `build_map.py`:

- City of Chicago Food Inspections Socrata API
- Dataset ID: `4ijn-s7e5`
- Fields: `dba_name, facility_type, latitude, longitude`
- Filter:
  - latitude is not null
  - longitude is not null
  - facility type contains `grocery`, `convenience`, or `supermarket`
- Deduplication:
  - same store name
  - within 35 meters
- Sort:
  - by store name

The original Python file also had:

```python
MAX_STORES_FOR_TESTING = 75
```

The website loads the full deduped set by default, but there is an **Original first 75** button if you want to match that original testing limit.

## Important limitation

GitHub Pages cannot run Python or call OpenRouteService from your server. So the green areas are approximate 12-minute walking circles, not exact street-network isochrone polygons.

The store data itself is still from the original City of Chicago source/filter.

## Optional: create a CSV with pandas

This is optional. The website does not need the CSV because it fetches the city data directly in the browser.

To create `grocery_stores.csv` locally:

```bash
pip install -r requirements.txt
python make_grocery_csv.py
```

This writes:

```text
grocery_stores.csv
grocery_stores_original_75.csv
```
