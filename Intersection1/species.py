

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
import matplotlib as mpl
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches


# load grid data and species data to process user input
grid = gpd.read_file(os.path.abspath('data/SpeciesData.shp'))
bird_details = pd.read_csv('data/SpeciesAttributes.csv') # species attributes for table linking


# Create a dictionary from the column names mapping DataFrame
bird_details_dict = dict(zip(bird_details['Code'], bird_details['Common_name']))




print("\nWelcome to BirdTrials!") 



while True:
    # Prompt user for input
    userselected = input("\nPlease enter a species code, for example 'kiwbro' for Kiwi, or enter 'list' for to return a list of codes and species: \n")

    # see if user requested the list
    if userselected.lower() == 'list':
        print(f'\nCode:    Species:')
        # set a spacing length to hopefully make the bird list look a bit better
        max_key_length = 9
        # print the dictionary as a lisdt, with spacing
        for key, value in bird_details_dict.items():
           spacing = ' ' * (max_key_length - len(key))
           print(f'{key}{spacing}{value}')
        continue


    # Check if the entered bird name exists
    if userselected in grid.columns:
        print("")
        break
    else:
        print("Sorry. This species does not exist (in the data available)")


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
trails = gpd.read_file(os.path.abspath('data/Trails.shp'))


# NZ outline added using cartopys ShapelyFeature
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', linewidth=0.3, facecolor='white')
xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature) # add the features we've created to the map.


# using the boundary of the shapefile features, zoom the map to our area of interest
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=myCRS) # because total_bounds 
# gives output as xmin, ymin, xmax, ymax,
# but set_extent takes xmin, xmax, ymin, ymax, we re-order the coordinates here.



# Define the colormap for the choropleth
cmap = mpl.colormaps['BuPu']  # Choose a suitable colormap

# Get the minimum and maximum values of 'birdocc' for normalization
min_value = min(grid[userselected])
max_value = max(grid[userselected])

# Normalize the 'birdocc' values to the range [0, 1]
normalised_values = [(value - min_value) / (max_value - min_value) for value in grid[userselected]]

# Create a list of facecolors based on the normalized values
facecolors = [cmap(value) for value in normalised_values]

# Create the ShapelyFeature with the modified facecolors
grid_feat = ShapelyFeature(grid['geometry'],
                           myCRS,
                           edgecolor='k',
                           facecolor=facecolors,
                           linewidth=0.2)


# plot won't work, but it does make a nice legend on the document
grid.plot(column=userselected,
   cmap='BuPu',
   linewidth=0.2,
   ax=ax,
   edgecolor='1',
   legend=True)
 

# select the index and relevant bird column
species_column = grid.columns.get_loc(userselected) # get a numerical value for the bird column

# make a copy of the grid gdf and sort it by the highest value of occupancy for selected bird
grid_sort = grid.iloc[:,:].copy()
grid_sorted = grid_sort.sort_values(by=f'{userselected}', axis=0, ascending=False)






# a loop that will run down the sorted grid data, from highest species occupancy until a intersect returns a True with a trail

found_intersection = False
iteration = 1

while not found_intersection:
    grid_hv_id = grid_sorted.iloc[iteration, :].copy() 
    
    intersection = trails['geometry'].intersects(grid_hv_id['geometry'])
    
    if any(intersection):
        found_intersection = True
    else:
        print(f'No trails found in grid {iteration}')
        iteration += 1 


# identify and print the grid attributes that intersect line.
print('Intersected trail IDs:')
intersect_id = [i for i, val in enumerate(intersection) if val]
print(intersect_id)


# create feature to highlight grids intercepted by track
intercepted_trails = trails[trails.index.isin(intersect_id)]

intercepted_trails_geometry = ShapelyFeature(intercepted_trails['geometry'],  # first argument is the geometry
 myCRS,  # second argument is the CRS
 edgecolor='red',  # set the edgecolor to be royalblue
 facecolor='none',  # hopefully stops the multi-line being filled in
 linewidth=1.5)  # set the linewidth to be 0.2 pt



ax.add_feature(grid_feat)  # add the collection of features to the map
ax.add_feature(intercepted_trails_geometry)


# Rename the columns in birdstats gdf using the dictionary
grid.rename(columns=bird_details_dict, inplace=True)
us_bird = bird_details_dict[userselected]



print("\nTrail details----------------------") 
print(f'Name: {userselected}') 
print(f'Description: {trails[(trails.name == userselected)].iloc[0, 2]}')
print(f'Difficulty: {trails[(trails.name == userselected)].iloc[0, 3]}')
print(f'Time: {trails[(trails.name == userselected)].iloc[0, 4]}')
print(f'Length: {traildistance.round(2)} km')
print(f'More information: {trails[(trails.name == userselected)].iloc[0, 7]}')



# Trail data
toplist = intercepted_trails.head(5) # Limit to 5 trails
# print("\nTrail information") 
# print(toplist)

# Create the table
table_data = [[str(toplist.tolist()[i]) + '%', str(toplist.index[i])] for i in range(len(toplist.tolist()))]
table = ax.table(cellText=table_data, loc='upper left', cellLoc='left', colLabels=['Occupancy', 'Species'], edges='open')
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(0.20, 1.5)  # Adjust the table size if needed

# add the title to the map, need to configure to display specifics
plt.title(f'{us_bird} bird occupancy')

# add the scale bar to the axis
scale_bar(ax)
# ax.add_feature(grid) # add the features we've created to the map.



myFig ## re-draw the figure

myFig.savefig(f'{us_bird} species map.png', bbox_inches='tight', dpi=300)



# Confirm map 
print("\nOverview map saved") 
print(f'.../{us_bird} species map.png') 




