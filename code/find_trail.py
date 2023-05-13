"""BirdTrails/find_trail.py generates a Folium map showing NZ trails.

This script uses Folium and Geopandas to load a data set of Department
of Conservation trails in New Zealand and display them on an interactive
HTML map. This will allow users to browse trails that can then be analysed
using by_bird.py


"""

import geopandas as gpd
import folium

 # load the Trail dataset and tidy the information for display on the map
data = gpd.read_file('data/Trails.shp') # load the data
data['length'] = data['SHAPE_Leng'] / 1000 # convert the lenth value from m to km
data['length'] = data['length'].round(2)  # round length to 2 decimal places
data['length'] = data['length'].astype(str) + ' km'  # change length data type to string and adds unit

m = folium.Map([-40, 174], zoom_start=5) # create map, focused on New Zealand

# processes the trail data as a GeoJson layer
# adapted from here https://anitagraser.com/2019/10/31/interactive-plots-for-geopandas-geodataframe-of-linestrings/
data_geojson = folium.GeoJson(data[data.geometry.length > 0.001],
  style_function=lambda feature: {
   'weight': 3,
   'color': 'red'
  },
  tooltip=folium.GeoJsonTooltip(sticky=False,
                                fields=['name', 'difficulty', 'completion', 'length'],
                                labels=True, aliases=['Trail name', 'Difficulty', 'Completion time', 'Trail length']))
# adds a tooltip function to the map, showing trail info on mouseover. Uses 'alias' parameter to tidy the labels on the tooltip
# from here https://python-visualization.github.io/folium/modules.html#folium.features.GeoJsonTooltip

# adds data to map
data_geojson.add_to(m)

m.save('user/Trail_maps.html') # saves the map
print('Map saved as .../user/Trail_maps.html') # confirms to user where the map has been saved

