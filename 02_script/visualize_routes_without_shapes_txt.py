import os
import json
import geojson
import pandas as pd
import folium
import webbrowser

# GTFS folder location
input_folder = r'D:\dev\github\GTFS_Visualization\01_source\KMRL-Open-Data'

output_folder = r'D:\dev\github\GTFS_Visualization\03_temp' # to store temporary file

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
list_agency = textToList(input_path_agencyTxt)
list_routes = textToList(input_path_routesTxt)
list_trips = textToList(input_path_tripsTxt)
list_stop_times = textToList(input_path_stopTimes)
list_stops = textToList(input_path_stopsTxt)

def sort_stop_sequence(e):
  return e['stop_sequence']


list_stop_times.sort(key=sort_stop_sequence)
print('sort_end')

dct_1 = {}
for items in list_stop_times:
    if items['trip_id'] not in dct_1:
        dct_1[items['trip_id']] = [items['stop_id']]
    else:
        dct_1[items['trip_id']].append(items['stop_id'])
print('dct1_end')

dct_2 = {}
for items in list_trips:
    if items['route_id'] not in dct_2:
        dct_2[items['route_id']] = [items['trip_id']]
    else:
        dct_2[items['route_id']].append(items['trip_id'])


l_1 = []
print('start')
for key,value in dct_2.items():
    for i in value:
        for k,v in dct_1.items():
            dct_3 = {}
            if i == k:
                dct_3['route'] = key
                dct_3['stops'] = v
                dct_3['trip_id'] = k
                for r in list_routes:
                    if key == r['route_id']:
                        # dct_3['route_color'] = r['route_color']
                        dct_3['route_color'] = '00B7F3'
                        break
                l_1.append(dct_3)
                break

print('l_1_end')

# for key, value in dct_1.items():
#     print('{}: {}'.format(key, len(value)))

unique_route = []
cnt = 0
for i in l_1:
    if cnt == 0:
        unique_route.append({'route': i['route'], 'stops': i['stops'], 'route_color': i['route_color']})
    cnt += 1    
    for j in unique_route:
        if (str(i['route']) == str(j['route']) and str(i['stops']) == str(j['stops'])):
            chck = 1
    if chck == 0:
        unique_route.append({'route': i['route'], 'stops': i['stops'], 'route_color': i['route_color']})
    chck = 0

print('start')
new = []
for i in unique_route:
    li = []
    li_name = []
    dct_4 = {}
    start_stop = i['stops'][0]
    end_stop = i['stops'][-1]
    start_stop_name = 'dummy'
    end_stop_name = 'dummy'
    for j in i['stops']:
        for k in list_stops:
            if (j == start_stop and k['stop_id'] == start_stop):
                start_stop_name = k['stop_name']
            if (j == end_stop and k['stop_id'] == end_stop):
                end_stop_name = k['stop_name']
            if str(j) == str(k['stop_id']):
                li.append([k['stop_lon'], k['stop_lat']])
                break
    dct_4['routeId'] = i['route']
    dct_4['stops'] = i['stops']
    dct_4['geometry'] = li
    dct_4['from_to'] = '{} -> {}'.format(start_stop_name, end_stop_name)
    dct_4['routeColor'] = i['route_color']
    new.append(dct_4)
#print(new[0])

def shape_to_feature(routeId, fromTo, routeColor, geo):
    return {
        'type': 'Feature',
        'geometry': {'type':'LineString', 'coordinates': geo},
        'properties': {
            'route_id': routeId,
            'from_to': fromTo,
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
    shape_to_feature(i['routeId'], i['from_to'], i['routeColor'], i['geometry'])
    for i in new])

stops_geojson = geojson.FeatureCollection([
    stops_to_feature(i['stop_lon'], i['stop_lat'], i['stop_name'])
    for i in list_stops])

# write geojson
shapes_geojson_path = os.path.join(output_folder, 'shapes.geojson')
with open(shapes_geojson_path, 'w') as f:
   json.dump(shapes_geojson, f)

stops_geojson_path = os.path.join(output_folder, 'stops.geojson')
with open(stops_geojson_path, 'w') as f:
   json.dump(stops_geojson, f)

# initiate map object
m = folium.Map(
    #location = [10.0727,76.3336],
    #tiles='cartodbpositron',
    tiles = None,
    zoom_start = 16,
    control_scale = True)

# Adding map heading
map_heading = list_agency[0]['agency_name'].upper()
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(map_heading)
m.get_root().html.add_child(folium.Element(title_html))

# specifying properties from GeoJSON
shapes_style_function = lambda x: {
    'color': x['properties']['route_color'],
    'opacity': 1,
    'weight': '4',
    #'dashArray': '3,6'
}

shapes_highlight_function = lambda x: {
    'color': 'yellow',
    'opacity': 1,
    'weight': '6',
    #'dashArray': '3,6'
}

# Plotting geojson
stops_map = folium.features.GeoJson(
    stops_geojson_path,
    name = 'stops',
    control = True,
    tooltip= folium.features.GeoJsonTooltip(
        fields=['stop_name'],
        aliases=['Stop Name: '],
        # setting style for popup box
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
)

shapes_map = folium.features.GeoJson(
    shapes_geojson_path,
    name = 'shapes',
    control = True,
    style_function = shapes_style_function,
    highlight_function = shapes_highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        # using fields from the geojson file
        fields=['from_to', 'route_id'],
        aliases=['Route: ', 'Route_ID: '],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
  )
)

m.add_child(stops_map)
m.add_child(shapes_map)

# To zoom on data extent
m.fit_bounds(m.get_bounds(), padding=(30, 30))

# saving the map to html file and oppening it in default browser upon script execution
html_path = os.path.join(output_folder, 'map.html')
m.save(html_path)
webbrowser.open(html_path)