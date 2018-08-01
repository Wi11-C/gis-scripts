import os, sys, shutil, glob, re, time
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
from PyQt5.QtCore import QVariant

# Provide constants
local_gis_working_dir = os.path.join("C:", os.sep, "Users", "Will", "Desktop", "GIS")
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
                    with edit(out_layer):
                        out_layer.dataProvider().addFeature(pt)
                        # TODO: Figure out how to add attribute to feature before uploading feature to layer dataprovider
                    print (points_of_intersection.asWkt())
                    # line_layer_prime = QgsVectorLayer("LineString?crs=EPSG:102658&index=yes", "result1", "memory")
                    # line_layer_sub = QgsVectorLayer("LineString?crs=EPSG:102658&index=yes", "result2", "memory")
                    # with edit(line_layer_prime):
                    #     line_layer_prime.dataProvider().addFeature(road_feature)
                    # with edit(line_layer_sub):
                    #     line_layer_sub.dataProvider().addFeature(close_fid)

                    # print (points_of_intersection.asWkt())
    print ("Custom intersection pulled {} points".format(count))
    timer_end = time.time()
    print ("{} took {} seconds".format(create_intersection_points_layer.__name__, round(timer_end - timer_start, 2)))
    timer_start = time.time()

    params = {
        'INPUT': dissolved_road_layer,
        'INTERSECT': dissolved_road_layer,
        'INPUT_FIELDS':['NAME'],
        'INTERSECT_FIELDS':['NAME'],
        'OUTPUT':'memory:'
        }
    points_of_intersection_slow = processing.run("native:lineintersections", params)
    timer_end = time.time()
    print ("{} took {} seconds".format(create_intersection_points_layer.__name__, round(timer_end - timer_start, 2)))
    return points_of_intersection_slow

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
