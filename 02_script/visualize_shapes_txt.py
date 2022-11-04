import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import geojson
import json

# shapes.txt path
input_path = r"D:\dev\github\GTFS_Visualization\01_source\KMRL-Open-Data\shapes.txt"

# with open(input_path) as input_file:
#     for line in input_file:
#         temp_line = []
#         line = line.rstrip('\n')
#         temp_line = line.split(',')
#         input_list.append(temp_line)


# Conver shapes.txt into list
df = pd.read_csv(input_path)
list_1 = df.to_dict('records')

# Storing coordinates in dict as per 'shape_id'
dct_1 = {}
for items in list_1:

    if items['shape_id'] not in dct_1:
        dct_1[items['shape_id']] = [[items['shape_pt_lon'],items['shape_pt_lat']]]
    else:
        dct_1[items['shape_id']].append([items['shape_pt_lon'],items['shape_pt_lat']])

# Re-arranging dct_1 to new list for further use
output_list = []
for key,value in dct_1.items():
    d2 = {}
    d2['routeId'] = key
    d2['geometry'] = {'type':'LineString', 'coordinates': value}
    output_list.append(d2)

# convert above list to geojson
def route_to_feature(route, geo):
    return {
        'type': 'Feature',
        'geometry': geo,
        'properties': {
            'name': route
        }
    }

out_geojson = geojson.FeatureCollection([
    route_to_feature(i['routeId'], i['geometry'])
    for i in output_list])

# write geojson
out_geojson_path = r"D:\dev\github\GTFS_Visualization\03_temp\t1.geojson"
with open(out_geojson_path, 'w') as f:
   json.dump(out_geojson, f)

plt.rcParams.update({'axes.facecolor':'black'})
dta = gpd.read_file(out_geojson_path)

dta.plot(color="#f5f5f5")
#ax = plt.axes()
#ax.set_facecolor("yellow")

plt.title("Kochi Metro")

plt.show()
