import os
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


trails = gpd.read_file('data/Trails.shp')


m = trails.explore


m # show the map

m.save('Trails_map.html')

