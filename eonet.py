"""
Plot of all EONET (Earth Observatory Natural Event Tracker) events data in the last 365 days.

API: https://eonet.gsfc.nasa.gov/docs/v2.1/events
(There is also an Category-API.)
"""

import requests
import json
import plotly.express as px

limit = -1  # All events in period
days = 365  # last year
file_name = 'events_eonet.json'

try:
    # Read data
    with open(file_name) as f:
        events_data = f.readall()
except Exception:
    # Request data
    url = f'https://eonet.gsfc.nasa.gov/api/v2.1/events?limit={limit}&days={days}'
    r = requests.get(url)
    # Parse data
    events_data = r.json()
    # Save data
    with open(file_name, 'w') as f:
        f.write(json.dumps(events_data, indent=4))

# Extract coordinates from geoJSON and event title
longitudes, latitudes = [], []
hover_names = []
for event in events_data['events']:
    coordinates = event['geometries'][0]['coordinates']
    longitude, latitude = coordinates[0], coordinates[1]
    # Check consitency
    # Some coordinates are obvious switched and easily to filter but there is
    # also an iclandic volcano in the indian ocean.
    if -180 <= longitude <= 180 and -90 <= latitude <= 90:
        longitudes.append(longitude)
        latitudes.append(latitude)
        # Configure hover name
        title = event['title']
        category = event['categories'][0]['title']
        full_title = f'{title} [{category}]'
        hover_names.append(full_title)

# Plot
plot_data = {'Latitude': latitudes,
             'Longitude': longitudes,
             'Hover_names': hover_names}
fig = px.scatter_geo(plot_data,
                     lat='Latitude',
                     lon='Longitude',
                     hover_name='Hover_names')
fig.show()
