import os
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


trails = gpd.read_file('data/Trails.shp')
print(trails.head())

m = folium.Map([48.2, 16.4], zoom_start=10)
 
folium.Choropleth(
    trails[trails.geometry.SHAPE_leng>0.001],
    line_weight=3,
    line_color='blue'
).add_to(m)
 

folium.PolyLine(trails, tooltip="Coast").add_to(m)

m # show the map

m.save('Kea_map.html')