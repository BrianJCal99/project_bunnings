import pandas as pd
import plotly.express as px
import json
from rich import print

# --- Load data ---
df = pd.read_csv("output/bunnings_stores_20251022_000234.csv")

# Clean
df["State"] = df["State"].str.upper().str.strip()
df["Store Rating"] = pd.to_numeric(df["Store Rating"], errors="coerce")
df["Total Ratings"] = pd.to_numeric(df["Total Ratings"], errors="coerce")

# Aggregate per state
state_stats = (
    df.groupby("State")
    .agg(Average_Rating=("Store Rating", "mean"), Store_Count=("Store Name", "count"), Total_Ratings=("Total Ratings", "sum"))
    .reset_index()
)

# Map codes to full names matching the GeoJSON
state_name_map = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "SA": "South Australia",
    "WA": "Western Australia",
    "TAS": "Tasmania",
    "ACT": "Australian Capital Territory",
    "NT": "Northern Territory"
}
state_stats["State_Name"] = state_stats["State"].map(state_name_map)

print(state_stats)

# --- Load Australia GeoJSON ---
with open("data/australian-states.json") as f:
    geojson = json.load(f)

# --- Create Choropleth ---
fig = px.choropleth(
    state_stats,
    geojson=geojson,
    locations="State_Name",
    featureidkey="properties.STATE_NAME",  # must match field in geojson
    color="Average_Rating",  # or 'Store_Count'
    color_continuous_scale="Viridis",
    title="Average Bunnings Store Rating by State (Australia)",
    labels={"Average_Rating": "Avg Store Rating", "State_Name": "State", "Store_Count": "Number of Stores", "Total_Ratings": "Total Number of Ratings"},
    hover_name="State_Name",  # shows on hover
    hover_data={
        "Store_Count": True,
        "Average_Rating": ":.2f",  # format to 2 decimals
        "State_Name": False,       # avoid duplicate name
        "State": True,
        "Total_Ratings": True
    }
)

fig.update_geos(fitbounds="locations", visible=False)
fig.show()
