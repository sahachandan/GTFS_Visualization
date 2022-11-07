# Python: v3.9.13, OS: Windows 11

import os
import sys
import json
import random
import geojson
import folium
import webbrowser
import pandas as pd


# GTFS folder location
input_folder = r'D:\dev\github\GTFS_Visualization\01_source\Open_Data_MMTS_Hyd'

# Output folder location to store geojson, html files
output_folder = r'D:\dev\github\GTFS_Visualization\03_out'

# If basemap_on = 'y' OSM will appear as basemap
basemap_on = ''

def bcg_map():
    if basemap_on == 'y':
        return 'openstreetmap'
    else:
        return None

# Create output folder if not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Output file name prefix
output_file_prefix = 'script2_{}'.format(((input_folder.split('\\')[-1]).replace(' ','_')).lower())


# Reading text files
input_path_agencyTxt = os.path.join(input_folder, 'agency.txt')
input_path_routesTxt = os.path.join(input_folder, 'routes.txt')
input_path_tripsTxt = os.path.join(input_folder, 'trips.txt')
input_path_stopTimes = os.path.join(input_folder, 'stop_times.txt')
input_path_stopsTxt = os.path.join(input_folder, 'stops.txt')

# with open(input_path) as input_file:
#     for line in input_file:
#         temp_line = []
#         line = line.rstrip('\n')
#         temp_line = line.split(',')
#         input_list.append(temp_line)

# Text file to List
def textToList(text_file):
    t1 = pd.read_csv(text_file)
    l1 = t1.to_dict('records')
    return l1

# Conver text files into list
try:
    list_agency = textToList(input_path_agencyTxt)
    list_routes = textToList(input_path_routesTxt)
    list_trips = textToList(input_path_tripsTxt)
    list_stop_times = textToList(input_path_stopTimes)
    list_stops = textToList(input_path_stopsTxt)
except:
    print('''
    Error: File missing
    Make sure to run this script following files are available in input directory:
                1. agency.txt
                2. routes.txt
                3. trips.txt
                4. stops.txt
                5. stop_times.txt''')
    sys.exit()

# sorting up stop_times.txt based on stop_sequence
def sort_stop_sequence(e):
  return e['stop_sequence']
list_stop_times.sort(key=sort_stop_sequence)

# Update route_color if not exist in routes.txt
for i in list_routes:
    if not 'route_color' in i:
        i['route_color'] = "%06x" % random.randint(0, 0xFFFFFF)
    if 'route_color' in i:
        if (str(i['route_color']) == 'nan' or str(i['route_color']) == ''):
            i['route_color'] = "%06x" % random.randint(0, 0xFFFFFF)


# Storing list of Stops per Trips
dct_trip_stop = {}
for items in list_stop_times:
    if items['trip_id'] not in dct_trip_stop:
        dct_trip_stop[items['trip_id']] = [items['stop_id']]
    else:
        dct_trip_stop[items['trip_id']].append(items['stop_id'])


# Storing list of Trips per Routes
dct_route_trip = {}
for items in list_trips:
    if items['route_id'] not in dct_route_trip:
        dct_route_trip[items['route_id']] = [items['trip_id']]
    else:
        dct_route_trip[items['route_id']].append(items['trip_id'])

# Storing route_id, stop_id, trip_id, route_color in a new list
list_1 = []
for key,value in dct_route_trip.items():
    for i in value:
        for k,v in dct_trip_stop.items():
            dct_1 = {}
            if i == k:
                dct_1['route_id'] = key
                dct_1['stop_id'] = v
                dct_1['trip_id'] = k
                for r in list_routes:
                    if key == r['route_id']:
                        dct_1['route_color'] = r['route_color']
                        break
                list_1.append(dct_1)
                break


# Storing Routes with unique Stops in a new list
list_unique_route = []
cnt = 0
for i in list_1:
    if cnt == 0:
        list_unique_route.append({'route_id': i['route_id'], 'stop_id': i['stop_id'], 'route_color': i['route_color']})
    cnt += 1    
    for j in list_unique_route:
        if (str(i['route_id']) == str(j['route_id']) and str(i['stop_id']) == str(j['stop_id'])):
            chck = 1
    if chck == 0:
        list_unique_route.append({'route_id': i['route_id'], 'stop_id': i['stop_id'], 'route_color': i['route_color']})
    chck = 0

# Adding up stop_name, stop_location
list_all = []
for i in list_unique_route:
    lst_geo = []
    dct_2 = {}
    start_stop = i['stop_id'][0]
    end_stop = i['stop_id'][-1]
    start_stop_name = 'dummy'
    end_stop_name = 'dummy'
    for j in i['stop_id']:
        for k in list_stops:
            if (j == start_stop and k['stop_id'] == start_stop):
                start_stop_name = k['stop_name']
            if (j == end_stop and k['stop_id'] == end_stop):
                end_stop_name = k['stop_name']
            if str(j) == str(k['stop_id']):
                lst_geo.append([k['stop_lon'], k['stop_lat']])
                break
    dct_2['routeId'] = i['route_id']
    dct_2['stops'] = i['stop_id']
    dct_2['stop_count'] = len(i['stop_id'])
    dct_2['geometry'] = lst_geo
    dct_2['from_to'] = '{} TO {}'.format(start_stop_name, end_stop_name)
    dct_2['routeColor'] = i['route_color']
    list_all.append(dct_2)


# convert to geojson
def shape_to_feature(routeId, fromTo, stopCount, routeColor, geo):
    return {
        'type': 'Feature',
        'geometry': {'type':'LineString', 'coordinates': geo},
        'properties': {
            'route_id': routeId,
            'from_to': fromTo,
            'stop_count': stopCount,
            'route_color': '#{}'.format(routeColor)
        }
    }

def stops_to_feature(stop_lon, stop_lat, stop_name):
    return {
        'type': 'Feature',
        'geometry': {'type':'Point', 'coordinates': [stop_lon, stop_lat]},
        'properties': {
            'stop_name': stop_name
        }
    }

shapes_geojson = geojson.FeatureCollection([
    shape_to_feature(i['routeId'], i['from_to'], i['stop_count'], i['routeColor'], i['geometry'])
    for i in list_all])

stops_geojson = geojson.FeatureCollection([
    stops_to_feature(i['stop_lon'], i['stop_lat'], i['stop_name'])
    for i in list_stops])

# write geojson
shapes_geojson_path = os.path.join(output_folder, '{}_shapes.geojson'.format(output_file_prefix))
with open(shapes_geojson_path, 'w') as f:
   json.dump(shapes_geojson, f)

stops_geojson_path = os.path.join(output_folder, '{}_stops.geojson'.format(output_file_prefix))
with open(stops_geojson_path, 'w') as f:
   json.dump(stops_geojson, f)


# initiate map object
m = folium.Map(
    #location = [10.0727,76.3336],
    #tiles='cartodbpositron',
    tiles = bcg_map(),
    zoom_start = 16,
    control_scale = True)

shape_Layer = folium.FeatureGroup(name='shapes_geom').add_to(m)
stops_Layer = folium.FeatureGroup(name='stops_geom').add_to(m)

# Adding map heading
map_heading = list_agency[0]['agency_name'].upper()
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(map_heading)
m.get_root().html.add_child(folium.Element(title_html))

# specifying properties from GeoJSON
shapes_style_function = lambda x: {
    'color': x['properties']['route_color'],
    'opacity': 0.6,
    'weight': '4',
    #'dashArray': '3,6'
}

shapes_highlight_function = lambda x: {
    'color': 'yellow',
    'opacity': 1,
    'weight': '10',
    #'dashArray': '3,6'
}

# Plotting geojson
stops_map = folium.GeoJson(
    stops_geojson_path,
    name = 'stops',
    control = True,
    # marker = folium.Marker( # Radius in metres
    #                         icon_size = 0, #outline weight
    #                         icon = folium.Icon(color='darkblue'), 
    #                         fill_opacity = 1),
    tooltip= folium.GeoJsonTooltip(
        fields=['stop_name'],
        aliases=['Stop Name: '],
        # setting style for popup box
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
)

shapes_map = folium.GeoJson(
    shapes_geojson_path,
    name = 'shapes',
    control = True,
    style_function = shapes_style_function,
    highlight_function = shapes_highlight_function,
    tooltip=folium.GeoJsonTooltip(
        # using fields from the geojson file
        fields=['from_to', 'stop_count', 'route_id'],
        aliases=['Route: ', 'Total Stops: ', 'Route_ID: '],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
  )
)

shapes_map.add_to(shape_Layer)
stops_map.add_to(stops_Layer)

# m.add_child(stops_map)
# m.add_child(shapes_map)

folium.LayerControl().add_to(m)

# To zoom on data extent
m.fit_bounds(m.get_bounds(), padding=(30, 30))

# saving the map to html file and oppening it in default browser upon script execution
html_path = os.path.join(output_folder, '{}_map.html'.format(output_file_prefix))
m.save(html_path)
webbrowser.open(html_path)