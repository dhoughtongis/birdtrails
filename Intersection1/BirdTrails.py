

"""A one-line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""

import os
import pandas as pd
import geopandas as gpd
import cartopy
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches

# load trail data first to check user input
trails = gpd.read_file(os.path.abspath('data/Trails.shp'))

print("\nWelcome to BirdTrials!\n\nThis is a tool that...") 
print("\nIf you are unsure what trail you are interested in, you can use the TrailFinder or BirdFinder tools included in this package") 
while True:
    # Prompt user for input
    userselected = input("\nPlease enter a trail name, for example 'Milford Track': ")

    # Check if the entered trail name exists
    selected_trail = trails[trails['name'] == userselected]

    if not selected_trail.empty:
        print("")
        break
    else:
        print("The trail does not exist in the geodatabase. Please check for errors and try again.")
        
display_stats = input("\nExport a .csv with the bird occupancy data for this trail? (y/n): ")



# The intersect data is being truncated
# This -should- stop that. From https://www.geeksforgeeks.org/how-to-print-an-entire-pandas-dataframe-in-python/
pd.set_option('display.max_rows', 3000) 
pd.set_option('display.max_columns', 65)

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
outline = gpd.read_file(os.path.abspath('data/NZ_outline.shp'))
lakes = gpd.read_file(os.path.abspath('data/Lakes.shp'))
rivers = gpd.read_file(os.path.abspath('data/Rivers.shp'))


grid = gpd.read_file(os.path.abspath('data/SpeciesData.shp'))
bird_details = pd.read_csv('data/SpeciesAttributes.csv') # species attributes for table linking


# Create a dictionary from the column names mapping DataFrame
bird_details_dict = dict(zip(bird_details['Code'], bird_details['Common_name']))
# Rename the columns in birdstats DataFrame using the dictionary
grid.rename(columns=bird_details_dict, inplace=True)


# NZ outline added using cartopys ShapelyFeature
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', linewidth=0.3, facecolor='lightgreen')
lakes_feature = ShapelyFeature(lakes['geometry'], myCRS, edgecolor='paleturquoise', linewidth=0, facecolor='paleturquoise')
rivers_feature = ShapelyFeature(rivers['geometry'], myCRS, edgecolor='paleturquoise', linewidth=0.3, facecolor='none')
xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature) # add the features we've created to the map.
ax.add_feature(lakes_feature)
ax.add_feature(rivers_feature)

# using the boundary of the shapefile features, zoom the map to our area of interest
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS) # because total_bounds 
# gives output as xmin, ymin, xmax, ymax,
# but set_extent takes xmin, xmax, ymin, ymax, we re-order the coordinates here.




trails_feat = ShapelyFeature(trails['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 edgecolor='tan',  # set the edgecolor to be royalblue
 facecolor='none',  # hopefully stops the multi-line being filled in
 linewidth=0.2)  # set the linewidth to be 0.2 pt


selected_feat = ShapelyFeature(selected_trail['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 edgecolor='red',  # set the edgecolor to be royalblue
 facecolor='none',  # hopefully stops the multi-line being filled in
 linewidth=1)  # set the linewidth to be 0.2 pt
 


grid_feat = ShapelyFeature(grid['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 facecolor='none',  # sets the face color to coral, hopefully
 linewidth=0.2,  # set the outline width to be 1 pt
 alpha=0.75, # set the alpha (transparency) to be 0.25 (out of 1)
 edgecolor='gray')

# Find the intersection between the line and the polygon, save boolean of data as txt doc.
intersection = grid.intersects(selected_trail.unary_union)
# print(intersection,  file=open('log.txt', 'w')) # create a .txt file containing the full boolean list for troubleshooting

# identify and print the grid attributes that intersect line.
print('Intersected grid sectors:')
intersect_id = [i for i, val in enumerate(intersection) if val]
print(intersect_id)

# create feature to highlight grids intercepted by track
intercepted_grids = grid[grid.index.isin(intersect_id)]

intercepted_grids_geometry = ShapelyFeature(intercepted_grids['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 edgecolor='k',  # set the edgecolor to be royalblue
 facecolor='none',  # hopefully stops the multi-line being filled in
 linewidth=0.5)  # set the linewidth to be 0.2 pt



# Extract details of selected trails from dataset for analysis

# Convert trail distance from m to km
traildistance = trails[(trails.name == userselected)].iloc[0, 9] / 1000

print("\nTrail details----------------------") 
print(f'Name: {userselected}') 
print(f'Description: {trails[(trails.name == userselected)].iloc[0, 2]}')
print(f'Difficulty: {trails[(trails.name == userselected)].iloc[0, 3]}')
print(f'Time: {trails[(trails.name == userselected)].iloc[0, 4]}')
print(f'Length: {traildistance.round(2)} km')
print(f'More information: {trails[(trails.name == userselected)].iloc[0, 7]}')

# Bird stats



birdstats = grid.iloc[intersect_id, 10:73] * 100
birdstats.loc['Avg'] = birdstats.iloc[:, 1:].mean().round(2)




sorted_birdstats = birdstats.sort_values(by='Avg', axis=1, ascending=False)
toplist = sorted_birdstats.loc['Avg'].head(15)
# print("\nHighest bird presence along trail (%)----------------------") 
# print(toplist)



ax.add_feature(grid_feat)  # add the collection of features to the map
ax.add_feature(trails_feat)  # add the collection of features to the map
ax.add_feature(intercepted_grids_geometry)  # add the collection of features to the map
ax.add_feature(selected_feat)  # add the collection of features to the map


# Create the table
table_data = [[str(toplist.tolist()[i]) + '%', str(toplist.index[i])] for i in range(len(toplist.tolist()))]
table = ax.table(cellText=table_data, loc='upper left', cellLoc='left', colLabels=['Occupancy', 'Species'], edges='open')
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(0.20, 1.5)  # Adjust the table size if needed




# add the title to the map, need to configure to display specifics
plt.title(f'{userselected} bird occupancy')

# add the scale bar to the axis
scale_bar(ax)

# format a legend for the grid and tracks using proxy shapes
intersect_true = mpatches.Rectangle((0, 0), 1, 1, facecolor="k")
intersect_false = mpatches.Rectangle((0, 0), 1, 1, facecolor="gray")
labels = ['Grid square intersects \nwalking track',
   'Grid square does not \nintersect walking track']
plt.legend([intersect_true, intersect_false], labels,
   loc='lower right', bbox_to_anchor=(1, 0), fancybox=True)

   

myFig ## re-draw the figure

myFig.savefig(f'{userselected} overview.png', bbox_inches='tight', dpi=300)

# Confirm map 
print("\nOverview map saved") 
print(f'.../{userselected} overview.png') 


if display_stats.lower() == "y":
    birdstats.to_csv(f'{userselected} occupancy data.csv', index=False)
    print("\nOccupancy data saved")
    print(f'.../{userselected} occupancy data.csv')
else:
    print("\nOccupancy data not requested.")
    
