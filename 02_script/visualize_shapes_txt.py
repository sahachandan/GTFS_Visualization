import os
import json
import geojson
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# GTFS folder location
input_folder = r'D:\dev\github\GTFS_Visualization\01_source\KMRL-Open-Data'

output_folder = r'D:\dev\github\GTFS_Visualization\03_temp' # to store temporary file

# Reading text files
input_path_agencyTxt = os.path.join(input_folder, 'agency.txt')
input_path_routesTxt = os.path.join(input_folder, 'routes.txt')
input_path_tripsTxt = os.path.join(input_folder, 'trips.txt')
input_path_shapesTxt = os.path.join(input_folder, 'shapes.txt')

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

# Conver routes.txt into list
list_routes = textToList(input_path_routesTxt)

# Conver trips.txt into list
list_trips = textToList(input_path_tripsTxt)

# Conver shapes.txt into list
list_shape = textToList(input_path_shapesTxt)


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
            break
    output_list.append(d2)


# convert above list to geojson
def route_to_feature(routeId, shapeId, routeColor, geo):
    return {
        'type': 'Feature',
        'geometry': geo,
        'properties': {
            'route_id': routeId,
            'shape_id': shapeId,
            'route_color': routeColor
        }
    }

out_geojson = geojson.FeatureCollection([
    route_to_feature(i['routeId'], i['shapeId'], i['routeColor'], i['geometry'])
    for i in output_list])

# write geojson
out_geojson_path = os.path.join(output_folder, 't1.geojson')
with open(out_geojson_path, 'w') as f:
   json.dump(out_geojson, f)

plt.rcParams.update({'axes.facecolor':'black'})
dta = gpd.read_file(out_geojson_path)

dta.plot(color="#f5f5f5")
#ax = plt.axes()
#ax.set_facecolor("yellow")

plt.title("Kochi Metro")

plt.show()