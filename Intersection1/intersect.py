import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# The intersection data is being truncated
# This -should- stop that. From https://www.geeksforgeeks.org/how-to-print-an-entire-pandas-dataframe-in-python/
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3)

plt.ion() # make the plotting interactive

# generate matplotlib handles to create a legend of the features we put in our map.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the colort list
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

# load the outline of NZ for a backdrop
outline = gpd.read_file(os.path.abspath('data/NZ_outline.shp'))

# load the grid and trail data
grid = gpd.read_file(os.path.abspath('data/SpeciesData.shp'))
trails = gpd.read_file(os.path.abspath('data/Trails.shp'))



myFig = plt.figure(figsize=(10, 10))  # create a figure of size 10x10 (representing the page size in inches)

myCRS = ccrs.UTM(59, southern_hemisphere=True)  # create a Universal Transverse Mercator reference system to transform our data.

ax = plt.axes(projection=ccrs.NearsidePerspective(satellite_height=10000000.0, central_longitude=-174.88, central_latitude=-40.9))  # finally, create an axes object in the figure, using a UTM projection,
# where we can actually plot our data.

# NZ outline added using cartopys ShapelyFeature
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w')
xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature) # add the features we've created to the map.

# using the boundary of the shapefile features, zoom the map to our area of interest
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS) # because total_bounds 
# gives output as xmin, ymin, xmax, ymax,
# but set_extent takes xmin, xmax, ymin, ymax, we re-order the coordinates here.


trails_feat = ShapelyFeature(trails['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 edgecolor='tan',  # set the edgecolor to be royalblue
 facecolor='none',  # hopefully stops the multi-line being filled in
 linewidth=0.2)  # set the linewidth to be 0.2 pt

# trying to highlight selected track example is milford track
milford = trails[(trails.name == 'Milford Track')]


selected_feat = ShapelyFeature(milford['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 edgecolor='red',  # set the edgecolor to be royalblue
 facecolor='none',  # hopefully stops the multi-line being filled in
 linewidth=1)  # set the linewidth to be 0.2 pt



grid_feat = ShapelyFeature(grid['geometry'],  # first argument is the geometry
  myCRS,  # second argument is the CRS
  facecolor='coral',  # sets the face color to coral, hopefully
  linewidth=0.2,  # set the outline width to be 1 pt
  alpha=0.75, # set the alpha (transparency) to be 0.25 (out of 1)
  edgecolor='k' 
)  
# Don't know why the below isn't working 
# if ShapelyFeature(milford['geometry'],myCRS).intersects(ShapelyFeature(grid['geometry'],myCRS)) else 'lightgray'

# Check if and where the selected track intersects the grid

# reset the index of gdf2
# milford = milford.reset_index(drop=True)
# set the index of gdf2 to be the same as gdf1
# milford.index = grid.index

# Find the intersection between the line and the polygon
intersection = grid.intersects(milford.unary_union)
print(intersection,  file=open('log.txt', 'w'))

print(milford.index)
print(grid.index)




ax.add_feature(grid_feat)  # add the collection of features to the map
ax.add_feature(trails_feat)  # add the collection of features to the map
ax.add_feature(selected_feat)  # add the collection of features to the map


# add the title to the map, need to configure to display specifics
plt.title('Grid intersection)')

# add the scale bar to the axis
scale_bar(ax)

# format a legend using proxy shapes
intersect_true = mpatches.Rectangle((0, 0), 1, 1, facecolor="k")
intersect_false = mpatches.Rectangle((0, 0), 1, 1, facecolor="lightgray")
labels = ['Grid square intersects \nwwalking track',
   'Grid square does not \nintersect walking track']
plt.legend([intersect_true, intersect_false], labels,
   loc='lower right', bbox_to_anchor=(1, 0), fancybox=True)



myFig ## re-draw the figure

myFig.savefig('Milford_map.png', bbox_inches='tight', dpi=300)