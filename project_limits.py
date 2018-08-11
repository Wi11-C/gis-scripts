import os, sys, shutil, glob, re, time
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
from PyQt5.QtCore import QVariant
from env_config import config
from project_limits_helper import *
import ProjectLoader

# Provide constants

env = config()
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.2", True)
app = QgsApplication([], False)
QgsApplication.initQgis()

project = QgsProject.instance()
project.read(os.path.join(env.local_gis_working_dir, 'MakePackageMap.qgs'))

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

"""
Creates points on the first layer with a 'Name' attributre from the second layer where the two layers intersect 
"""
def create_intersection_points_layer(dissolved_road_layer, intersecting_line_layer, field_name):
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
                    loc_name = close_feature[field_name]
                    loc_feat = QgsFeature()
                    loc_feat.setGeometry(pt)
                    with edit(out_layer):
                        out_layer.dataProvider().addFeature(loc_feat)
                        out_layer.changeAttributeValue(feature_id_counter, 0, loc_name)
                        feature_id_counter += 1
    
    timer_end = time.time()
    print ("{} took {} seconds".format(create_intersection_points_layer.__name__, round(timer_end - timer_start, 2)))
    print ("{} points of intersection found".format(feature_id_counter))
   
    return out_layer

lay_roads = QgsVectorLayer(os.path.join(env.local_shape_dir, 'ENG.CENTERLINE.shp'), 'Roads', 'ogr')
print ("{} roads".format(CountFeatures(lay_roads))) 

# Load and reproject the LWDD Canal Layer before combining it with the road layer
# lay_canals = processing.run("native:reprojectlayer", {'INPUT':os.path.join(env.local_shape_dir, 'Export_LWDD.shp'),'TARGET_CRS':'EPSG:102658','OUTPUT':'memory:'})['OUTPUT']
# print ("{} canals".format(CountFeatures(lay_canals))) 

temp_dissolved_roads = dissolve_lines(lay_roads, 'STREET') #61985
# print ("{} dissolved roads".format(CountFeatures(temp_dissolved_roads))) 

# temp_dissolved_canals = dissolve_lines(lay_canals, 'CANAL_NAME')
# print ("{} dissolved canals".format(CountFeatures(temp_dissolved_canals))) 

# result_layer = combine_layers(temp_dissolved_roads, temp_dissolved_canals)
# print ("{} total".format(CountFeatures(result_layer))) 

print ('computing points for canals')
# intersection_points_canals = create_intersection_points_layer(temp_dissolved_roads, temp_dissolved_canals, 'CANAL_NAME')
print ('computing poitns for roads')
# intersection_points_roads = create_intersection_points_layer(temp_dissolved_roads, temp_dissolved_roads, 'NAME')

print ('combining point layers')
# points_of_intersection = processing.run("native:mergevectorlayers", {'LAYERS':[intersection_points_canals, intersection_points_roads], 'CRS':'ESPG:102658','OUTPUT':'memory'})
# print ("{} intersection points".format(CountFeatures(points_of_intersection))) 

# Save output
# provider = points_of_intersection.dataProvider()
# QgsVectorFileWriter.writeAsVectorFormat(points_of_intersection, r"C:\Users\Will\Desktop\test\test.gpkg", provider.encoding(), provider.crs())

project_names = ProjectLoader.LoadProjects(os.path.join(env.local_gis_working_dir, "projects.csv"))

error_count = 0
project_count = 0

for record in project_names:
    project_count += 1
    proj = ProjectLoader.ProjectName(record[1], record[0])
    if proj.has_errors:
        error_count += 1
    else:
        if proj.is_intersection:
            for road in temp_dissolved_roads.getFeatures():
                if road['STREET'].toString().lower() == proj.intersection_first_road.full_name.lower():
                    print ('Road: {} | Name: {}'.format(road['STREET'].toString(), proj.intersection_first_road.full_name))
        else:
            for road in temp_dissolved_roads.getFeatures():
                try: 
                    rd = road['STREET'].toString().lower()
                except:
                    try:
                        rd = road['STREET'].lower()
                    except:
                        print ('Error')
                        rd = ''
                if rd == proj.corridor.lower():
                    print('Road: {} | Name: {}'.format(rd, proj.corridor.full_name))


print ('{} projects, {} errors'.format(project_count, error_count))
    
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
