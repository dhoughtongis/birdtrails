import os
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines



trails = gpd.read_file('data/Trails.shp')





trails_df = gpd.GeoDataFrame(geometry=gpd)

trails.head() # show the new geodataframe


folium.LayerControl().add_to(m)

m # show the map

m.save('TrailPicker_map.html')