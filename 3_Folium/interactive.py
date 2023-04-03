import os
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


grid = gpd.read_file('data/SpeciesData.shp')


m = grid.explore('kea', cmap='Oranges')


m # show the map

m.save('Kea_map.html')

