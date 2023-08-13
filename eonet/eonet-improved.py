"""
Plot of all EONET (Earth Observatory Natural Event Tracker) events data in the last 365 days.

API: https://eonet.gsfc.nasa.gov/docs/v2.1/events
(There is also an Category-API.)
"""

from datetime import datetime
import requests
import json
import plotly.graph_objects as go


class EonetEvent():
    """Wrapper for an Eonet event."""

    def __init__(self, id, title, category, lon, lat):
        self.id = id
        self.title = title
        self.category = category
        self.lon = lon
        self.lat = lat


limit = -1  # All events in period
days = 365  # last year
file_names = ('eonet/eonet_data.json', 'eonet/categoryIDs_data_eonet.json')
data = []

# Fetch data (via request or read from file)
try:
    # Read data
    for file_name in file_names:
        with open(file_name) as f:
            data.append(f.readall())
except Exception:
    # Request data
    urls = (f'https://eonet.gsfc.nasa.gov/api/v2.1/events?limit={limit}&days={days}',
            'https://eonet.gsfc.nasa.gov/api/v2.1/categories')
    for url, file_name in zip(urls, file_names):
        r = requests.get(url)
        data_tmp = r.json()
        data.append(data_tmp)
        # Save data
        with open(file_name, 'w') as f:
            f.write(json.dumps(data_tmp, indent=4))
    events_data = data[0]
    categoryIDs_data = data[1]

# ID dict with colors
categoryID_color = {}
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#ff6600',
          '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#7f0000', '#003300',
          '#000033']
for i, category in enumerate(categoryIDs_data['categories']):
    categoryID_color[category['id']] = colors[i]
del categoryIDs_data

# Extract coordinates from geoJSON and event title
# TODO: Farben integrieren, da gerade zwei dicts mit id als Schlüssel
events_per_categoryID = {id: [] for id in categoryID_color}
for event in events_data['events']:
    coordinates = event['geometries'][0]['coordinates']
    longitude, latitude = coordinates[0], coordinates[1]
    # Check consitency
    # Some coordinates are obvious switched and easily to filter but there is
    # also an iclandic volcano in the indian ocean.
    if -180 <= longitude <= 180 and -90 <= latitude <= 90:
        # Encapsulate data
        title = event['title']
        category = event['categories'][0]['title']
        id = event['categories'][0]['id']
        eonet_event = EonetEvent(id, title, category, longitude, latitude)
        # Add event to dictionary
        events_per_categoryID[eonet_event.id].append(eonet_event)

# Plot data per category
fig = go.Figure()
# Iterate over all categoryIDs to configure a Scattergeo-object/plot
# Each category is colored differently
for categoryID, event_list in events_per_categoryID.items():
    # Collect longitudes, latitudes of all events in category
    longitudes, latitudes = [], []
    for event in event_list:
        longitudes.append(event.lon)
        latitudes.append(event.lat)
    # Normal scatter_geo function does not support category wise plotting,
    # so I have to use the Scattergeo-object
    fig.add_trace(go.Scattergeo(
        lon=longitudes,
        lat=latitudes,
        mode='markers',
        # because <mode='markers'> is used (and not 'lines')
        marker={'color': categoryID_color[categoryID],
                'size': 10},
        hovertext=event_list[0].title if event_list else "TODO",
        # Entry in legend
        name=event_list[0].category if event_list else "TODO",
    ))

date = datetime.now().date().strftime('%Y-%m-%d')
fig.update_layout(
    title_text=f'EONET (Earth Observatory Natural Event Tracker) events in the last {days} days, requested on {date}.',)
fig.show()
