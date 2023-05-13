"""BirdTrails/by_bird.py identies the routes with the highest occupancy of a user selected species

This script uses a bird occupancy dataset create a map showing a range of Department of 
Conservation trails in NZ that intersect high occupancy grids for a user selected species.#
It will sort the grid by decending order of the bird occupancy for the species, and then
use Shapely's 'intersects' clause to identify tracks that intersect with these grids.

It will produce a map showing a chloropleth of the bird's occupancy data across the grid,
along with the trails that are intersect these high presense areas.

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


# creates a dictionary to load the common names of the birds in the grid GeoDataFrame from the species attribute table
bird_details_dict = dict(zip(bird_details['Code'], bird_details['Common_name']))


print("\nWelcome to BirdTrials!") 


# user input to select a bird using its code, including an option to create a list of all specie codes and common names using the dictionary
while True:
    # prompt user for input
    userselected = input("\nPlease enter a species code, for example 'kiwbro' for Kiwi, or enter 'list' for to return a list of codes and species: \n")

    # see if the user requested the list
    if userselected.lower() == 'list':
        print(f'\nCode:    Species:')
        # set a spacing length to hopefully make the bird list look a bit better
        max_key_length = 9
        # print the dictionary as a lisdt, with spacing
        for key, value in bird_details_dict.items():
           spacing = ' ' * (max_key_length - len(key))
           print(f'{key}{spacing}{value}')
        continue


    # check the bird name exists, if not prompt user to try again
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
# adapted from iamdonovan's adaptation of this question: https://stackoverflow.com/q/32333870
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


# load the shapefiles data sets for country outline and Department of Conservation trails
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


# define a colourmap for the grid
cmap = mpl.colormaps['BuPu']  

# find the min and max value of the bird occupancy data for normalisation
min_value = min(grid[userselected])
max_value = max(grid[userselected])

# normalise the occupancy data and assign facecolours based on value
normalised_values = [(value - min_value) / (max_value - min_value) for value in grid[userselected]]
facecolors = [cmap(value) for value in normalised_values]


# create the ShapelyFeature with the colourmap assigned
grid_feat = ShapelyFeature(grid['geometry'],
  myCRS,
  edgecolor='k',
  facecolor=facecolors,
  linewidth=0.2)


# plot is now redundant, but it does make a nice colourmap legend on the exported map
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


# a loop that will run down the sorted grid data, from highest species occupancy until a stopping at the 50th intersection
# adapted from https://www.w3schools.com/python/python_for_loops.asp
# the loop will run one-by-one through the 50 grids with the highest occupancy value appending a boolean dataset
print('\nChecking hig occupancy grids for trails\n')
found_intersection = False
iteration = 1
intersection_list = []

while not found_intersection:
    grid_hv_id = grid_sorted.iloc[iteration, :].copy() 
    
    intersection = trails['geometry'].intersects(grid_hv_id['geometry'])
    i_id = [i for i, val in enumerate(intersection) if val]
    intersection_list.append(i_id)
    
    if any(intersection):
        print(f'Trail in grid {iteration}: yes')
        # found_intersection = True # activating this will stop the loop at the first intersection found
        iteration += 1
    else:
        print(f'Trail in grid {iteration}: no')
        iteration += 1
        
    if iteration == 50: # activating this will stop the loop at iteration/grid
        break


# identify and print the grid attributes that intersect line. Activate for troubleshooting
# print(intersection_list)


# clean up the compiled intersection list (i_id), by removing groupings and repeat occurences of numbers.
# gives us a list of the grids intersected by trails in order of highest occupancy value
intersect_id = []
seen_values = set()

for sublist in intersection_list:
    for value in sublist:
        if value not in seen_values:
            intersect_id.append(value)
            seen_values.add(value)


# trim the list to 15
print('\nIdentified track IDs in order of presence in higher bird occupany area')
# print(intersect_id) # troubleshooting
intersect_id_trimmed = intersect_id[:15]
print(intersect_id_trimmed)


# create feature to highlight grids intersected by track, limited to top 15
unsorted_intersect = trails[trails.index.isin(intersect_id_trimmed)]
intersected_trails = unsorted_intersect.sort_values(by='name', axis=0, ascending=True)
# print(intersected_trails) # troubleshooting


# Trying to get individual colours for each line.
# range of 15 colours compatable with the grid's colormap to identify each trail
trailcolours = ['Red', 'Crimson', 'Maroon', 'Tomato', 'Coral', 'Gold', 'Yellow', 'LemonChiffon', 'LimeGreen', 'Green', 'OliveDrab', 'Chartreuse', 'MediumSeaGreen', 'ForestGreen', 'DarkGreen']

intersected_trails_geometry = ShapelyFeature(intersected_trails['geometry'],  # first argument is the geometry
  myCRS,  # second argument is the CRS
  edgecolor=trailcolours,  # set the edgecolor to be defined
  facecolor='none',  # hopefully stops the multi-line being filled in
  linewidth=3)  # set the linewidth

# add the species specific chloropleth grid and intersected trails to map
ax.add_feature(grid_feat)  
ax.add_feature(intersected_trails_geometry)


# Rename the columns in birdstats GDF using the dictionary
grid.rename(columns=bird_details_dict, inplace=True)
us_bird = bird_details_dict[userselected]


# Trail data
toplist = intersected_trails.iloc[:,:].head(15) # Limit to 15 trails
toplist['SHAPE_Leng'] = toplist['SHAPE_Leng'] / 1000 # convert trail length in this list from m to km
toplist['SHAPE_Leng'] = toplist['SHAPE_Leng'].round(1) # round to 1 decimal point
# print(toplist) # troubleshoot if needed


# Create the table. colour text in the table, same order as the trail geometry colours
table_data = [[str(toplist['SHAPE_Leng'].iloc[i]) + 'km', str(toplist['name'].iloc[i])] for i in range(len(toplist))]
table = ax.table(cellText=table_data, 
                 loc='upper left', 
                 cellColours=[['Red', 'White'],
                              ['Crimson', 'White'],
                              ['Maroon', 'White'],
                              ['Tomato', 'White'],
                              ['Coral', 'White'],
                              ['Gold', 'White'],
                              ['Yellow', 'White'],
                              ['LemonChiffon', 'White'],
                              ['LimeGreen', 'White'],
                              ['Green', 'White'],
                              ['OliveDrab', 'White'],
                              ['Chartreuse', 'White'],
                              ['MediumSeaGreen', 'White'],
                              ['ForestGreen', 'White'],
                              ['DarkGreen', 'White']],
                 cellLoc='left', 
                 colLabels=['Length', 'Trail name'])
table.auto_set_font_size(False)
table.set_fontsize(7) # smaller font, as trail names can be quite long
table.scale(0.15, 1.55)  # Adjust the table size if needed
for key, cell in table.get_celld().items():
    cell.set_linewidth(0)



# add the title to the map, need to configure to display specifics
plt.title(f'{us_bird} occupancy with trails')


# add the scale bar to the axis
scale_bar(ax)


myFig ## re-draw the figure


myFig.savefig(f'user/{us_bird} species map.png', bbox_inches='tight', dpi=300)


# print track detail list, with websites and improved spacing
print(f'\nTracks with highest {us_bird} occupancy/presence') 
for index, row in toplist.iterrows():
    list_name = row['name']
    list_web = row['walkingAnd']
    list_distance = row['SHAPE_Leng']
    list_completion = row['completion']
    print(f"\nName:       {list_name}\nDistance:   {list_distance} km\nCompletion: {list_completion}\nWebsite:    {list_web}")


# Confirm map export to user, with location
print("\nOverview map saved") 
print(f'.../user/{us_bird} species map.png') 




