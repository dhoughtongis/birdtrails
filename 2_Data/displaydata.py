import os
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

plt.ion() # make the plotting interactive

# generate matplotlib handles to create a legend of the features we put in our map.
def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the colort list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

# create a scale bar of length 50km
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

grid_feat = ShapelyFeature(grid['geometry'],  # first argument is the geometry
  myCRS,  # second argument is the CRS
  edgecolor='k',  # outline the feature in black
  facecolor='coral',  # sets the face color to the corral, hopefully
  linewidth=1,  # set the outline width to be 1 pt
  alpha=0.75)  # set the alpha (transparency) to be 0.25 (out of 1)
ax.add_feature(grid_feat)  # add the collection of features to the map

trails_feat = ShapelyFeature(trails['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 edgecolor='royalblue',  # set the edgecolor to be royalblue
 facecolor='none',  # hopefully stops the multi-line being filled in
 linewidth=0.2)  # set the linewidth to be 0.2 pt
ax.add_feature(trails_feat)  # add the collection of features to the map

# add the scale bar to the axis
scale_bar(ax)

myFig ## re-draw the figure



myFig.savefig('map.png', bbox_inches='tight', dpi=300)