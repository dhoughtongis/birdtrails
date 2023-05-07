import os
import pandas as pd
import geopandas as gpd
import cartopy
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches


plt.ion() # make the plotting interactive

# generate matplotlib handles to create a legend of the features we put in our map.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

# create a scale bar of length 200km
# adapted this question: https://stackoverflow.com/q/32333870
# answered by SO user Siyh: https://stackoverflow.com/a/35705477
def scale_bar(ax, location=(0.92, 0.95)):
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    ax.plot([sbx, sbx - 200000], [sby, sby], color='k', linewidth=9, transform=ax.projection)
    ax.plot([sbx, sbx - 100000], [sby, sby], color='k', linewidth=6, transform=ax.projection)
    ax.plot([sbx-100000, sbx - 200000], [sby, sby], color='w', linewidth=6, transform=ax.projection)

    ax.text(sbx, sby-42000, '200 km', transform=ax.projection, fontsize=6)
    ax.text(sbx-102500, sby-42000, '100 km', transform=ax.projection, fontsize=6)
    ax.text(sbx-204500, sby-42000, '0 km', transform=ax.projection, fontsize=6)

myFig = plt.figure(figsize=(10, 10))  # create a figure of size 10x10 (representing the page size in inches)

myCRS = ccrs.UTM(59, southern_hemisphere=True)  # create a Universal Transverse Mercator reference system to transform our data.

ax = plt.axes(projection=ccrs.NearsidePerspective(satellite_height=10000000.0, central_longitude=-174.88, central_latitude=-40.9))  # finally, create an axes object in the figure, using a UTM projection,
# where we can actually plot our data.

# load the shapefiles data sets for species, trails and country outline
land_use = gpd.read_file(os.path.abspath('data/lu/LandUse.shp'))







land_use_colors = ['darkgreen', 'green', 'orange', 'blue', 'lightseagreen', 'yellow', 'white']

land_use_id = list(land_use.gridcode.unique())
land_use_id.sort()

for ii, name in enumerate(land_use_id):
    lane_use_feat = ShapelyFeature(land_use.loc[land_use['gridcode'] == name, 'geometry'],
                                   myCRS,
                                   edgecolor='k',
                                   facecolor=land_use_colors[ii],
                                   linewidth=0)











plt.title(' Error map')


# format a legend for the grid and tracks using proxy shapes
intersect_true = mpatches.Rectangle((0, 0), 1, 1, facecolor="k")
intersect_false = mpatches.Rectangle((0, 0), 1, 1, facecolor="lightgray")
labels = ['Grid square intersects \nwalking track',
   'Grid square does not \nintersect walking track']
plt.legend([intersect_true, intersect_false], labels,
   loc='lower right', bbox_to_anchor=(1, 0), fancybox=True)

   

myFig ## re-draw the figure

myFig.savefig(' Mapoverview.png', bbox_inches='tight', dpi=300)

