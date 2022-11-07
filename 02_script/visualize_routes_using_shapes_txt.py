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
input_folder = r'D:\dev\github\GTFS_Visualization\01_source\KMRL_Open_Data'

# Output folder location to store geojson, html files
output_folder = r'D:\dev\github\GTFS_Visualization\03_out'

# if 'y' OSM will appear as basemap
basemap_on = 'y'

def bcg_map():
    if basemap_on == 'y':
        return 'openstreetmap'
    else:
        return None

# Create output folder if not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Output file name prefix
output_file_prefix = 'script1_{}'.format(((input_folder.split('\\')[-1]).replace(' ','_')).lower())


# Reading text files
input_path_agencyTxt = os.path.join(input_folder, 'agency.txt')
input_path_routesTxt = os.path.join(input_folder, 'routes.txt')
input_path_tripsTxt = os.path.join(input_folder, 'trips.txt')
input_path_shapesTxt = os.path.join(input_folder, 'shapes.txt')
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
    list_shape = textToList(input_path_shapesTxt)
    list_stops = textToList(input_path_stopsTxt)
except:
    print('''
    Error: File missing
    Make sure to run this script following files are available in input directory:
                1. agency.txt
                2. routes.txt
                3. trips.txt
                4. stops.txt
                5. shapes.txt''')
    sys.exit()


# Update route_color if not exist in routes.txt
for i in list_routes:
    if not 'route_color' in i:
        i['route_color'] = "%06x" % random.randint(0, 0xFFFFFF)
    if 'route_color' in i:
        if (str(i['route_color']) == 'nan' or str(i['route_color']) == ''):
            i['route_color'] = "%06x" % random.randint(0, 0xFFFFFF)


# Listing unique route_id per shape_id
unique_shape_list = []
cnt = 0
for i in list_trips:
    # print(i['route_id'])
    if cnt == 0:
        unique_shape_list.append({'route_id':i['route_id'], 'shape_id':i['shape_id']})
    cnt += 1    
    for j in unique_shape_list:
        if (str(i['route_id']) == str(j['route_id']) and str(i['shape_id']) == str(j['shape_id'])):
            chck = 1
    if chck == 0:
        unique_shape_list.append({'route_id':i['route_id'], 'shape_id':i['shape_id']})
    chck = 0

# Adding route_color from routes.txt
unique_shape_list_clr = []
for h in unique_shape_list:
    for r in list_routes:
        dct_1 = {}
        if (h['route_id'] == r['route_id']):
            dct_1['route_id'] = h['route_id']
            dct_1['route_long_name'] = r['route_long_name']
            dct_1['shape_id'] = h['shape_id']
            dct_1['route_color'] = r['route_color']
            unique_shape_list_clr.append(dct_1)
            break

# Storing coordinates in dict as per 'shape_id'
dct_1 = {}
for items in list_shape:
    if items['shape_id'] not in dct_1:
        dct_1[items['shape_id']] = [[items['shape_pt_lon'],items['shape_pt_lat']]]
    else:
        dct_1[items['shape_id']].append([items['shape_pt_lon'],items['shape_pt_lat']])


# Re-arranging dct_1 to new list for further use
output_list = []
for key,value in dct_1.items():
    d2 = {}
    d2['shapeId'] = key
    d2['geometry'] = {'type':'LineString', 'coordinates': value}
    for i in unique_shape_list_clr:
        if d2['shapeId'] == i['shape_id']:
            d2['routeId'] = i['route_id']
            d2['routeColor'] = i['route_color']
            d2['route_long_name'] = i['route_long_name']
            break
    output_list.append(d2)


# convert to geojson
def shape_to_feature(routeId, shapeId, routeLongName, routeColor, geo):
    return {
        'type': 'Feature',
        'geometry': geo,
        'properties': {
            'route_id': routeId,
            'shape_id': shapeId,
            'route_long_name': routeLongName,
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
    shape_to_feature(i['routeId'], i['shapeId'], i['route_long_name'], i['routeColor'], i['geometry'])
    for i in output_list])

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
    'weight': '8',
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
        fields=['route_long_name', 'route_id'],
        aliases=['Route: ', 'Route_ID: '],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
  )
)

m.add_child(stops_map)
m.add_child(shapes_map)

# To zoom on data extent
m.fit_bounds(m.get_bounds(), padding=(30, 30))

# saving the map to html file and oppening it in default browser
html_path = os.path.join(output_folder, '{}_map.html'.format(output_file_prefix))
m.save(html_path)
webbrowser.open(html_path)