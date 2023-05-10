import geopandas as gpd
import folium

# Read the shapefile
data = gpd.read_file('data/Trails.shp')

m = folium.Map([48.2, 16.4], zoom_start=10)

# Create a GeoJson layer
geojson = folium.GeoJson(data[data.geometry.length > 0.001],
                         style_function=lambda feature: {
                             'weight': 3,
                             'color': 'blue'
                         },
                         tooltip=folium.GeoJsonTooltip(fields=['name', 'difficulty', 'completion', 'SHAPE_Leng'], labels=True))

geojson.add_to(m)

m.save('Kea_map.html')

# Open the generated HTML file for editing
with open('Kea_map.html', 'r') as file:
    html_content = file.read()

# Add the custom JavaScript code
javascript_code = """
<script>
function copyToClipboard(text) {
    var input = document.createElement('textarea');
    input.value = text;
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    alert('Copied to clipboard: ' + text);
}

function addCopyButton() {
    var trails = document.getElementsByClassName('leaflet-interactive');
    for (var i = 0; i < trails.length; i++) {
        var trail = trails[i];
        trail.onclick = function() {
            var trailName = this.getAttribute('data-original-title');
            copyToClipboard(trailName);
        };
        trail.setAttribute('data-toggle', 'tooltip');
        trail.setAttribute('data-placement', 'top');
        trail.setAttribute('title', 'Click to copy trail name');
    }
}

window.onload = addCopyButton;
</script>
"""

html_content = html_content.replace('</body>', javascript_code + '</body>')

# Save the modified HTML file
with open('Kea_map.html', 'w') as file:
    file.write(html_content)