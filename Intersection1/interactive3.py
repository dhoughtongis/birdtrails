import os
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


grid = gpd.read_file('data/SpeciesData.shp')
trails = gpd.read_file('data/Trails.shp')

# Iterate through each country boundary
for index, row in grid.iterrows():

    # Check if the country boundary intersects the line
    if row.geometry.intersects(trails):

        # If it does, add the country boundary to the map in a different color
        folium.GeoJson(row.geometry.__geo_interface__,
                       style_function=lambda x: {'color': 'red', 'fillOpacity': 0.1}).add_to(m)
    else:

        # If it doesn't, add the country boundary to the map in the default color
        folium.GeoJson(row.geometry.__geo_interface__).add_to(m)



trails_df = gpd.GeoDataFrame(geometry=gpd)

trails.head() # show the new geodataframe


folium.LayerControl().add_to(m)

m # show the map

m.save('Species_map.html')