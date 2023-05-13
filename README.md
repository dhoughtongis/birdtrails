# BirdTrails

Using geographical tools in Python to identify the relationship between trails and bird occupancy data in New Zealand.

## Data licensing

**New Zealand 1:50k Hydrography Data**

[Land Information New Zealand](https://data.linz.govt.nz/ )

[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)

**Occupancy Data**

[Manaaki Whenua – Landcare Research](https://datastore.landcareresearch.co.nz/)

[CC-BY-NC 4.0 (Attribution-NonCommercial) ](https://creativecommons.org/licenses/by-nc/4.0/)

**DOC Tracks**

[Department of Conservation Open Spatial Data](https://doc-deptconservation.opendata.arcgis.com/)

[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)

## Installation

BirdTrails includes a “environment.yml” file containing all the packages used in the code. Once Anaconda Navigator has opened select the Environments tab on the left, select ‘import’ at the bottom of the environments panel and the ‘import new environment’ window will open. Use the folder button to navigate to the BirdTrails fork saved on your computer and select the ‘environment.yml’ file in the root folder. Select import and Anaconda will install the packages and dependencies required for BirdTrails to work.

There are 3 Python scripts in the ‘code’ folder, each with a specific 
purpose:

1. find_trail.py: creates an interactive Folium map allowing users to explore and identify the DOC trails.
2. by_trail.py: analyses occupancy data along a chosen trail, identifying the birds with the highest presence. 
3. by_bird.py: uses occupancy data to identify the tracks with the highest presence of a bird selected by the user.

These can be launched from within a Python shell. 

Exported maps/data will be saved in the *user* folder.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)