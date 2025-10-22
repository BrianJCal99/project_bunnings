import pandas as pd
import geopandas as gpd
import plotly.express as px
from rich import print

state_code="SA"  # e.g., "NSW", "VIC", "QLD", etc.

# Load your store data
df = pd.read_csv("output/bunnings_stores_20251022_000234.csv")

# Clean suburb names (trim, uppercase/lowercase consistency)
df["Suburb"] = df["Suburb"].str.strip().str.upper()

# Aggregate by suburb (within state):
suburb_stats = (
    df.groupby(["State","Suburb"])
      .agg(Average_Rating=("Store Rating", "mean"),
           Store_Count=("Store Name","count"),
           Total_Ratings=("Total Ratings","sum"))
      .reset_index()
)

gdf = gpd.read_file("data/suburb-2-sa.geojson")

# Clean the name field in gdf so you can match:
gdf["SUBURB_NAME"] = gdf["sa_local_2"].str.strip().str.upper()  # replace as per your data

# Merge (left join) your stats into the geodata:
gdf2 = gdf.merge(suburb_stats[suburb_stats["State"]==state_code],
                 left_on="SUBURB_NAME", right_on="Suburb",
                 how="left")

# --- MODIFICATIONS FOR GREY 'NO STORE' SUBURBS ---

# 1. Create a categorical column for coloring.
# Suburbs with stores will have their rating converted to a string (rounded to one decimal).
# Suburbs without stores (NaN rating) will be marked with the string 'No Stores'.
gdf2['Rating_Category'] = gdf2['Average_Rating'].apply(
    lambda x: f'{x:.1f}' if pd.notna(x) else 'No Stores'
)

# 2. Define the discrete color map, mapping 'No Stores' to 'white'.
color_map = {'No Stores': 'white'}

# 3. Get unique *actual* ratings to define a color sequence.
rating_values = sorted(
    [r for r in gdf2['Rating_Category'].unique() if r != 'No Stores'],
    key=float
)

# Use a continuous color scale (Viridis) to generate discrete colors for the ratings.
if rating_values:
    colors = px.colors.sample_colorscale("Viridis", [n/(len(rating_values)-1) for n in range(len(rating_values))] if len(rating_values) > 1 else [0])
    
    # Update the color map with the generated colors for the specific rating strings
    for rating, color in zip(rating_values, colors):
        color_map[rating] = color

# 4. Create the choropleth map using the categorical column and discrete map.
fig = px.choropleth(
    gdf2,
    geojson=gdf2.geometry,
    locations=gdf2.index,
    color="Rating_Category", # Use the new categorical column
    hover_name="SUBURB_NAME",
    custom_data=[],
    hover_data={
        "Store_Count": True,
        "Average_Rating": ":.1f",
        "Total_Ratings": True,
    },
    labels={"SUBURB_NAME": "Suburb", "Average_Rating": "Avg Store Rating", "Store_Count": "Number of Stores"},
    title=f"Bunnings Stores in {state_code} – Suburb Average Rating Map",
    color_discrete_map=color_map, # Map 'No Stores' to 'white' and ratings to gradient
    category_orders={"Rating_Category": rating_values + ['No Stores']} # Ensure correct order in legend
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_selections(marker_line_width=0.5, marker_line_color='grey')
fig.update_layout(legend_title_text='Average Store Rating')
fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br><br>" +
                  "Stores: %{customdata[0]}<br>" + 
                  "Average Rating: %{customdata[1]}</br>" +
                  "Total Ratings: %{customdata[2]}<extra></extra>"
)
fig.show()
