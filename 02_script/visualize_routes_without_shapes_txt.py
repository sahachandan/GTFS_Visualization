import os
import json
import geojson
import pandas as pd
import folium
import webbrowser

# GTFS folder location
input_folder = r'D:\dev\github\GTFS_Visualization\01_source\open data_hmrl_June2022'

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

dct_1 = {}
for items in list_stop_times:
    if items['trip_id'] not in dct_1:
        dct_1[items['trip_id']] = [items['stop_id']]
    else:
        dct_1[items['trip_id']].append(items['stop_id'])


dct_2 = {}
for items in list_trips:
    if items['route_id'] not in dct_2:
        dct_2[items['route_id']] = [items['trip_id']]
    else:
        dct_2[items['route_id']].append(items['trip_id'])


l_1 = []

for key,value in dct_2.items():
    for i in value:
        for k,v in dct_1.items():
            dct_3 = {}
            if i == k:
                dct_3['route'] = key
                dct_3['stops'] = v
                dct_3['trip_id'] = k
                l_1.append(dct_3)

# for key, value in dct_1.items():
#     print('{}: {}'.format(key, len(value)))

unique_route = []
cnt = 0
for i in l_1:
    if cnt == 0:
        unique_route.append({'route': i['route'], 'stops': i['stops']})
    cnt += 1    
    for j in unique_route:
        if (str(i['route']) == str(j['route']) and str(i['stops']) == str(j['stops'])):
            chck = 1
    if chck == 0:
        unique_route.append({'route': i['route'], 'stops': i['stops']})
    chck = 0
print(unique_route)

