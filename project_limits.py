import os, sys, shutil, glob, re, time
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
from PyQt5.QtCore import QVariant

# Provide constants
local_gis_working_dir = os.path.join("C:", os.sep, "Users", os.getlogin(), "Desktop", "GIS")
local_shape_dir = os.path.join(local_gis_working_dir, "NEWDB")
geopackage_name = "RoadDB.gpkg"
local_geopackage_path = os.path.join(local_gis_working_dir, geopackage_name)
network_dir = os.path.join("C:", os.sep, "Users", "Will", "Desktop", "GIS", "Network")
network_geopackage_path = os.path.join(network_dir, geopackage_name)


QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.2", True)
app = QgsApplication([], False)
QgsApplication.initQgis()

project = QgsProject.instance()
project.read(os.path.join(local_gis_working_dir, 'MakePackageMap.qgs'))

sys.path.append(r'C:\Program Files\QGIS 3.2\apps\qgis\python\plugins')
from processing.core.Processing import Processing
Processing.initialize()
import processing
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

# --------------------------------------------

def dissolve_lines(layer, common_attribute):
    params = {
        'INPUT':layer,
        'FIELD':[common_attribute],
        'OUTPUT': 'memory:' # Make temp layer for export
        }
    dict_output = processing.run("native:dissolve", params)
    dissolved_line_layer = dict_output['OUTPUT']
    return dissolved_line_layer

def combine_layers(dissolved_roads_layer, dissolved_canals_layer):
    out_layer = QgsVectorLayer("LineString?crs=EPSG:102658&index=yes", "result", "memory")
    out_layer.dataProvider().addAttributes([QgsField("NAME", QVariant.String,'text',80)])
    out_layer.updateFields()
    feature_id_counter = 1
    with edit(out_layer):
        for f in dissolved_roads_layer.getFeatures():
            f_name = f['STREET']
            f_geometry = f.geometry()
            f_small = QgsFeature()
            f_small.setGeometry(f_geometry)
            out_layer.dataProvider().addFeatures([f_small])
            out_layer.changeAttributeValue(feature_id_counter, 0, f_name)
            feature_id_counter += 1
        for f in dissolved_canals_layer.getFeatures():
            f_name = f['CANAL_NAME']
            f_geometry = f.geometry()
            f_small = QgsFeature()
            f_small.setGeometry(f_geometry)
            out_layer.dataProvider().addFeatures([f_small])
            out_layer.changeAttributeValue(feature_id_counter, 0, f_name)
            feature_id_counter += 1
    return out_layer

def create_intersection_points_layer(dissolved_road_layer, intersecting_line_layer):
    print ('Making points')
    timer_start = time.time()
    feature_id_counter = 1
    out_layer = QgsVectorLayer("Point?crs=EPSG:102658&index=yes", "result", "memory")
    out_layer.dataProvider().addAttributes([QgsField("NAME", QVariant.String,'text',80)])
    feature_index = QgsSpatialIndex(intersecting_line_layer.getFeatures())

    for road_feature in dissolved_road_layer.getFeatures():
        features_close_to_subject_road = feature_index.intersects(road_feature.geometry().boundingBox()) #Index will only accept rectange
        for close_fid in features_close_to_subject_road:
            close_feature = intersecting_line_layer.getFeature(close_fid)
            if (close_feature.geometry().intersects(road_feature.geometry())):                           #Possible bounding boxes collide but not features themselves
                if not close_feature.geometry().equals(road_feature.geometry()):                         #We may run a layer against itself. Don't match feature to itself
                    pt = road_feature.geometry().intersection(close_feature.geometry())
                    loc_name = close_feature['CANAL_NAME']
                    loc_feat = QgsFeature()
                    loc_feat.setGeometry(pt)
                    with edit(out_layer):
                        x = out_layer.dataProvider().addFeature(loc_feat)
                        out_layer.changeAttributeValue(feature_id_counter, 0, loc_name)
                        feature_id_counter += 1
    
    timer_end = time.time()
    print ("{} took {} seconds".format(create_intersection_points_layer.__name__, round(timer_end - timer_start, 2)))
    print ("{} points of intersection found".format(feature_id_counter))
   
    return out_layer

# def points_intersection_slow(road_layer, intersect_layer):
#     feature_id_counter = 0
#     timer_start = time.time()

#     params = {
#         'INPUT': dissolved_road_layer,
#         'INTERSECT': intersecting_line_layer,
#         'INPUT_FIELDS':['NAME'],
#         'INTERSECT_FIELDS':['CANAL_NAME'],
#         'OUTPUT':'memory:'
#         }
#     points_of_intersection_slow = processing.run("native:lineintersections", params)['OUTPUT']
#     timer_end = time.time()
#     print ("{} took {} seconds".format(create_intersection_points_layer.__name__, round(timer_end - timer_start, 2)))
#     feature_id_counter = 0
#     for f in points_of_intersection_slow.getFeatures():
#         feature_id_counter += 1
#     print ("{} points of intersection found".format(feature_id_counter))
#     return

# def make_points(layer):

#     return point_layer

lay_roads = QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp'), 'Roads', 'ogr')
count = 0

for fea in lay_roads.getFeatures():
    count += 1

print ("{} roads".format(count)) 

# Load and reproject the LWDD Canal Layer before combining it with the road layer
lay_canals = processing.run("native:reprojectlayer", {'INPUT':os.path.join(local_shape_dir, 'Export_LWDD.shp'),'TARGET_CRS':'EPSG:102658','OUTPUT':'memory:'})['OUTPUT']

count = 0

for fea in lay_canals.getFeatures():
    count += 1

print ("{} canals".format(count)) 
temp_dissolved_roads = dissolve_lines(lay_roads, 'STREET')
count = 0

for fea in temp_dissolved_roads.getFeatures():
    count += 1

print ("{} dissolved roads".format(count)) 
temp_dissolved_canals = dissolve_lines(lay_canals, 'CANAL_NAME')
count = 0

for fea in temp_dissolved_canals.getFeatures():
    count += 1

print ("{} dissolved canals".format(count)) 

result_layer = combine_layers(temp_dissolved_roads, temp_dissolved_canals)
count = 0

for fea in result_layer.getFeatures():
    count += 1

print ("{} total".format(count)) 

points_of_intersection = create_intersection_points_layer(temp_dissolved_roads, temp_dissolved_canals)
# points_of_intersection_slow(temp_dissolved_roads, temp_dissolved_canals)

count = 0
for fea in points_of_intersection.getFeatures():
    count += 1

print ("{} intersection points".format(count)) 

# Save output
# provider = result_layer.dataProvider()
# QgsVectorFileWriter.writeAsVectorFormat(result_layer, r"C:\Users\Will\Desktop\test\test.gpkg", provider.encoding(), provider.crs())
# points_provider = points_of_intersection.dataProvider()
# QgsVectorFileWriter.writeAsVectorFormat(points_of_intersection, r"C:\Users\Will\Desktop\test\points.gpkg", points_provider.encoding(), points_provider.crs())

print ('-----------------------')
print ('Done!')

# New Temp layer with roads dissolved by name
# New Temp layer with canals dissolved by name
# Add Points on line with intersecting road names

# for each project
# select feature > ponts which intersect feature are placed in new layer
# select limit points into new layer
# new temp layer for line
# split lines by points
# find line which intersects both points (this is the line between the start and end)
# add line feature to new layer and assign project name and number to it
