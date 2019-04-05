import os, sys, shutil, glob, re, time
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
from PyQt5.QtCore import QVariant
from env_config import config
from project_limits_helper import CountFeatures
import ProjectLoader

# Provide constants

env = config()
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.4", True)
app = QgsApplication([], False)
QgsApplication.initQgis()

project = QgsProject.instance()
project.read(os.path.join(env.local_gis_working_dir, 'MakePackageMap.qgs'))

sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis\python\plugins')
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

def remove_blanks(input_layer):
    with edit(input_layer):
        for r in input_layer.getFeatures():
            if r['STREET'] == NULL:
                input_layer.deleteFeature(r.id())
    return input_layer

def get_point(point_layer, name):
    for point in point_layer.getFeatures():
        if name == point['NAME']:
            return point
    return None

def get_line_feature(road_layer, name):
    for rd in road_layer.getFeatures():
        if name.full_name == rd['STREET']:
            return rd
    return None

def make_layers_for_op(feat_rd, arr_feats_pt):
    temp_road_layer = QgsVectorLayer("Line?crs=EPSG:102658&index=yes", "temproad", "memory")
    temp_point_layer = QgsVectorLayer("Point?crs=EPSG:102658&index=yes", "temppoints", "memory")
    with edit(temp_road_layer):
        temp_road_layer.dataProvider().addFeature(feat_rd)
    with edit(temp_point_layer):
        for pt in arr_feats_pt:
            temp_point_layer.dataProvider().addFeature(pt)
    return temp_road_layer, temp_point_layer

lay_roads = QgsVectorLayer(os.path.join(env.local_shape_dir, 'ENG.CENTERLINE.shp'), 'Roads', 'ogr')
print ("{} roads".format(CountFeatures(lay_roads))) 

# Load and reproject the LWDD Canal Layer before combining it with the road layer
lay_canals = processing.run("native:reprojectlayer", {'INPUT':os.path.join(env.local_shape_dir, 'Export_LWDD.shp'),'TARGET_CRS':'EPSG:102658','OUTPUT':'memory:'})['OUTPUT']
print ("{} canals".format(CountFeatures(lay_canals))) 

temp_dissolved_roads = dissolve_lines(lay_roads, 'STREET')
print ("{} dissolved roads".format(CountFeatures(temp_dissolved_roads))) 
dissolved_roads = remove_blanks(temp_dissolved_roads)
print ("{} dissolved roads".format(CountFeatures(dissolved_roads))) 

print ('computing points for canals')
intersection_points_canals = create_intersection_points_layer(temp_dissolved_roads, lay_canals, 'CANAL_NAME')
print ('computing points for roads')
intersection_points_roads = create_intersection_points_layer(temp_dissolved_roads, temp_dissolved_roads, 'NAME')

# print ('combining point layers')
points_of_intersection = processing.run("native:mergevectorlayers", {'LAYERS':[intersection_points_canals, intersection_points_roads], 'CRS':'ESPG:102658','OUTPUT':'memory'})['OUTPUT']
print ("{} intersection points".format(CountFeatures(points_of_intersection))) 

# Save output
provider = points_of_intersection.dataProvider()
QgsVectorFileWriter.writeAsVectorFormat(points_of_intersection, r"C:\Users\Will\Desktop\test\test.gpkg", provider.encoding(), provider.crs())

project_names = ProjectLoader.LoadProjects(os.path.join(env.local_gis_working_dir, "projects.csv"))

error_count = 0
project_count = 0

def record_to_layers(road_layer, point_layer, record):
    proj = ProjectLoader.ProjectName(record[1], record[0])
    if proj.has_errors:
        return []
    rd = None
    pt1 = None
    pt2 = None
    temp_road_layer = None
    temp_point_layer = None
    if proj.is_intersection:
        rd = get_line_feature(dissolved_roads, proj.intersection_first_road)
        # filter only those points on the line feature
        pt1 = get_point(points_of_intersection, proj.intersection_second_road)
        if ((rd is None) or (pt1 is None)):
            print ('Error: Not all features not found')
            return []
        else:
            temp_road_layer, temp_point_layer = make_layers_for_op(rd, [pt1])
    else:
        rd = get_line_feature(dissolved_roads, proj.corridor)
        pt1 = get_point(points_of_intersection, proj.start)
        pt2 = get_point(points_of_intersection, proj.end)
        if ((rd is None) or (pt1 is None) or (pt2 is None)):
            print ('Error: Not all features not found')
            return []
        else:
            temp_road_layer, temp_point_layer = make_layers_for_op(rd, [pt1, pt2])
    
    return [temp_road_layer, temp_point_layer]     

for record in project_names:
    project_count += 1
    arr_layers = record_to_layers(dissolved_roads, points_of_intersection, record)
    if len(arr_layers) == 2:
        print ('SUCCESS: Rd:{} pts:{}'.format(CountFeatures(arr_layers[0]), CountFeatures(arr_layers[1])))
    else:
        error_count += 1     
        

        # if proj.is_intersection:
        #     for road in temp_dissolved_roads.getFeatures():
        #         if road['STREET'].upper() == proj.intersection_first_road.full_name:
        #             with edit(temp_road_layer):
        #                 temp_road_layer.dataProvider().addFeature(road)
        #             point = get_point(points_of_intersection, road['STREET'])

        #             print ('Road: {} | Name: {}'.format(road['STREET'].upper(), proj.intersection_first_road.full_name))
        # else:
        #     for road in temp_dissolved_roads.getFeatures():
        #         try: 
        #             rd = road['STREET'].upper()
        #         except:
        #             try:
        #                 rd = road['STREET'].toString().upper()
        #             except:
        #                 print ('Error')
        #                 rd = ''
        #         if rd == proj.corridor.full_name.upper():
        #             print('Road: {} | Name: {}'.format(rd.upper(), proj.corridor.full_name))


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
