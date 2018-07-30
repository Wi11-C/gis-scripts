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

def PushToNetwork():
    print ('Pushing Geopackage to network')
    if os.path.exists(network_geopackage_path):
        print ('Removing old Geopackage from network')
        os.remove(network_geopackage_path)
    print ('Copying Geopackage to network')
    shutil.copy2(local_geopackage_path, network_geopackage_path)
    return

def Make_geopackage(Arr_layers):
    print ('Making Geopackage')
    feedback = QgsProcessingFeedback()
    # for layer in Arr_layers:
        # print ('Packaging new layer')
        # ret = processing.run("native:package", { 'LAYERS' : layer, 'OUTPUT' : local_geopackage_path, 'OVERWRITE' : False }, feedback=feedback)
        # output = ret['OUTPUT']
        # print (output)
    ret = processing.run("native:package", { 'LAYERS' : Layers_to_package, 'OUTPUT' : local_geopackage_path, 'OVERWRITE' : False }, feedback=feedback)
    # print(feedback)
    # output = ret['OUTPUT']
    # print (output)
    return

def Add_township_section_to_geopackage():
    print ('Making Township-Section map layer')
    params = {
        'FIELD': ['RNGTWN'],
        'INPUT' : os.path.join(local_shape_dir, 'ORTHO_GRID_PY.shp'),
        'OUTPUT' : 'ogr:dbname="' + local_geopackage_path + '" table="RANGE-TOWNSHIP" (geom) sql='
    }
    processing.run("qgis:dissolve", params)
    print ('Local Geopackage updated')
    return

QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.2", True)
app = QgsApplication([], False)
QgsApplication.initQgis()

project = QgsProject.instance()
project.read(os.path.join(local_gis_working_dir, 'MakePackageMap.qgs'))

# print(project.fileName())
# active_layers = project.mapLayers()
# for l in active_layers:
#     print (l)

sys.path.append(r'C:\Program Files\QGIS 3.2\apps\qgis\python\plugins')
from processing.core.Processing import Processing
Processing.initialize()
import processing
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

# algs = QgsApplication.processingRegistry().algorithms()
# print ('-----these are the algs-----')
# for a in algs:
#     print(a.id)

# print ('-----This is the alg we are looking for-----')
# if QgsApplication.processingRegistry().algorithmById('native:package') != None:
#     print ('SUCCESS!!!!')
# else:
#     print ('Alg not found')


# if os.path.exists(local_geopackage_path):
# 	print ('Removing old Local Geopackage')
# 	os.remove(local_geopackage_path)


# lay = QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.RIGHT_OF_WAY.shp'), 'ENG.RIGHT_OF_WAY', 'ogr')
# local = QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\''), 'Local Roads', 'ogr')
# tfare = QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\''), 'Throughfare Roads', 'ogr')
# commission_districts = QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql=', 'Commdist', 'arcgisfeatureserver')
# epermits = QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 'ePermits', 'arcgisfeatureserver')
# Layers_to_package = [
#     QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.RIGHT_OF_WAY.shp'), 'ENG.RIGHT_OF_WAY', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.ROAD_PROJECTS.shp'), 'ENG.ROAD_PROJECTS', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.SIGNAL_PTS_MULTI.shp'), 'ENG.SIGNAL_PTS_MULTI', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.TIM_FUTURE_TFARE_LINE.shp'), 'ENG.TIM_FUTURE_TFARE_LINE', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'Export_LWDD.shp'), 'LWDD', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'ORTHO_GRID_PY.shp'), 'ROW Roll Maps', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'PAO.PARCELS.shp'), 'PAO.PARCELS', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'PAO.SUBDIVISIONS.shp'), 'PAO.SUBDIVISIONS', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'PZB_LU_APP_DATA.shp'), 'PZB_LU_APP_DATA', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'PZB.LU_APP.shp'), 'PZB.LU_APP', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'PZB.ZONING_APPS_PENDING.shp'), 'PZB.ZONING_APPS_PENDING', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'WUD_LG.ASBUILT_PY.shp'), 'WUD_LG.ASBUILT_PY', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.RPRESSURIZEDMAIN.shp'), 'WUD.RPRESSURIZEDMAIN', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.SSGRAVITYMAIN.shp'), 'WUD.SSGRAVITYMAIN', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.SSMANHOLE.shp'), 'WUD.SSMANHOLE', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.SSPRESSURIZEDMAIN.shp'), 'WUD.SSPRESSURIZEDMAIN', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.WPRESSURIZEDMAIN.shp'), 'WUD.WPRESSURIZEDMAIN', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\''), 'Local Roads', 'ogr'),
#     QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\''), 'Throughfare Roads', 'ogr'),
#     QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql=', 'Commission Districts', 'arcgisfeatureserver'),
#     QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 'ePermits', 'arcgisfeatureserver')
#     ]

raster_outline_geopacakge_name = 'old_projects'
raster_outline_geopackage_path = os.path.join(r'C:/Users/Will/Desktop', raster_outline_geopacakge_name) + '.gpkg'
first_run = True
total_tiffs = 0
georeferenced_tiffs = 0
captured_tiffs = 0
tiffs_outside_domain = 0
duplicates_purged = 0

def correct_link(Link): #For some reason the links are stored as python paths with doubble slashes...which need to be changed to single slashes in the attribute field
    corrected_link = Link.replace('\\\\', '\\')
    return corrected_link

def add_properties_to_new_feature(proj_no, proj_name, sheet_no):
    global first_run
    outline_layer = QgsVectorLayer(raster_outline_geopackage_path, raster_outline_geopacakge_name, 'ogr') #the default layer name is the name of the package
    if (first_run):
        outline_layer.dataProvider().addAttributes([QgsField("PROJ_NO", QVariant.String), QgsField("PROJ_NAME", QVariant.String), QgsField("Sheet", QVariant.String)])
        outline_layer.updateFields()
        first_run = False
    else:
        outline_layer.setSubsetString('"PROJ_NO" IS NULL OR "PROJ_NO" IS \'\'') #only return newly added features

    features = outline_layer.getFeatures()
    outline_layer.setSubsetString('')
    for f in features:
        with edit(outline_layer):
            outline_layer.changeAttributeValue(f.id(), 1, correct_link(f[1]))
            outline_layer.changeAttributeValue(f.id(), 2, proj_no) #the second argument is the index for the field with "PROJ_NO"
            outline_layer.changeAttributeValue(f.id(), 3, proj_name)
            outline_layer.changeAttributeValue(f.id(), 4, sheet_no)
    return

def Add_Rater_outline_to_geopackage(image_path, proj_name):
    lay = QgsRasterLayer(image_path)
    lay.setCrs(QgsCoordinateReferenceSystem('EPSG:102658'))
    params = {
        'LAYERS':[lay],
        'PATH_FIELD_NAME':'link',
        'ABSOLUTE_PATH':False,
        'PROJ_DIFFERENCE':False,
        'TARGET_CRS':'EPSG:102658',
        'CRS_FIELD_NAME':'',
        'CRS_FORMAT':0,
        'OUTPUT': raster_outline_geopackage_path
    }
    processing.run("gdal:tileindex", params)
    return

def get_proj_name_and_number_from_folder(folder):
    root, folder = os.path.split(folder)
    # arr_folder_name = re.split(r'\W+', folder, 1)
    arr_folder_name = re.search(r'([a-zA-Z0-9]+)[\W|_]+([a-zA-Z0-9].+)',folder)
    proj_no = arr_folder_name[1].strip()
    proj_name = arr_folder_name[2].strip()
    return proj_no, proj_name

def get_sister_file_name(tif_file_path):
    sister_file_name = re.sub(r'.tif$', '.tfw', tif_file_path, 1, re.IGNORECASE)
    return sister_file_name

def get_sheet_no(tif_file_path):
    try:
        sheet_number = re.search(r'(?:sheet\s+)(\w+)', tif_file_path, re.IGNORECASE).group(0)
    except AttributeError:
        sheet_number = ''
        print ('No sheet number for the following file: ' + tif_file_path)
    return sheet_number

def get_proj_no(tif_file_path):
    proj_no = re.search(r'\w+', tif_file_path).group(0)
    return proj_no

def index_folder(folder_path):
    global total_tiffs
    global georeferenced_tiffs
    global captured_tiffs
    folder_total_tiffs = 0
    folder_georef_tifs = 0
    folder_captured_tiffs = 0
    proj_no_from_folder, proj_name = get_proj_name_and_number_from_folder(folder_path)

    files = glob.glob(os.path.join(folder_path, "*.tif")) #glib is case insensative by default
    for f in files:
        folder_total_tiffs += 1
        total_tiffs += 1
        sister_file_name = get_sister_file_name(f)
        if (os.path.isfile(sister_file_name)):
            folder_georef_tifs += 1
            georeferenced_tiffs += 1
            root, file_name = os.path.split(f)
            proj_no = get_proj_no(file_name)
            sheet_no = get_sheet_no(file_name)
            if (sheet_no == ''): #If there is a TIF that doesn't have a sheet number, there's a good chance it's name is just a random number...therefore overwrite projNo with folder Project No
                print ('Folder_proj_no: ' + proj_no_from_folder)
                proj_no = proj_no_from_folder
            if (proj_no != ''):
                folder_captured_tiffs += 1
                captured_tiffs += 1
                Add_Rater_outline_to_geopackage(f, proj_name)
                add_properties_to_new_feature(proj_no, proj_name, sheet_no)
    try:
        capture_eff = captured_tiffs/total_tiffs * 100
    except ZeroDivisionError:
        capture_eff = 0
    print ("Total: {} Geo: {} Captured: {} {}%".format(folder_total_tiffs, folder_georef_tifs, folder_captured_tiffs, round(capture_eff, 1)))
    return

def process_project_dir(project_directory_path):
    old_project_folder_paths = os.listdir(project_directory_path)
    total_folders = len(old_project_folder_paths)
    current_folder_count = 0
    for f in old_project_folder_paths:
        root, folder = os.path.split(f)
        current_folder_count += 1
        print ("({} of {}) {}".format(current_folder_count, total_folders, folder))
        index_folder(os.path.join(project_directory_path,f))
    return

def remove_duplicates(layer):
    global duplicates_purged
    allfeatures={}
    index = QgsSpatialIndex()
    for ft in layer.getFeatures():
        allfeatures[ft.id()] = ft
        index.insertFeature(ft)

    selection = []
    dict_dupes = {}
    for feat in layer.getFeatures():
        idsList = index.intersects(feat.geometry().boundingBox())
        if len(idsList) > 1:
            
            for id in idsList:

                # print (allfeatures[id].geometry())

                if (allfeatures[id].geometry().equals(feat.geometry())):
                    if (id != feat.id()):
                        if (int(id) > int(feat.id())):
                            larger_id = id
                            smaller_id = feat.id()
                        else:
                            larger_id = feat.id()
                            smaller_id = id
                        if (not (smaller_id in dict_dupes) or (dict_dupes[smaller_id] != larger_id)):
                            duplicates_purged += 1
                            dict_dupes[ "{}--{}".format(smaller_id, larger_id)] = True
                            
    for key in sorted(dict_dupes.items()):
        print ("Match: {}".format(key[0]))
    # for k in selection:
    #     print (k.id())
    print ('Duplicate Tiffs Purged: {}'.format(duplicates_purged))
    return

def shapes_outside_domain(layer):
    global tiffs_outside_domain
    feature_ids_of_tiffs_outside_domain = []
    
    rect = QgsRectangle(661133.3, 717146.6, 982541.7, 7964236.2)
    county_boundry_geometry = QgsGeometry.fromRect(rect)

    for raster_feature in layer.getFeatures():
        if not raster_feature.geometry().intersects(county_boundry_geometry):
            print ('{} lies outside the boundry'.format(raster_feature.id()))
            tiffs_outside_domain += 1
            feature_ids_of_tiffs_outside_domain.append(raster_feature.id())
    return feature_ids_of_tiffs_outside_domain

def remove_features_by_id(layer, arr_feature_ids):
    total_removed = 0
    with edit(layer):
        for f in layer.getFeatures():
            if f.id() in arr_feature_ids:
                layer.deleteFeature(f.id())
                total_removed += 1
    print ("Total Features remvoved {}".format(total_removed))
    return

# process_project_dir(r'F:\Internal-E\Work\TRENCH')
# process_project_dir(r'F:\Internal-E\Work\Non-trench Projects')
# process_project_dir(r'F:\Internal-E\Work\AlreadyGIS')

# layer_containing_some_dups = QgsVectorLayer(raster_outline_geopackage_path, raster_outline_geopacakge_name, 'ogr') #the default layer name is the name of the package
# feature_ids_to_remove = shapes_outside_domain(layer_containing_some_dups)
# remove_features_by_id(layer_containing_some_dups, feature_ids_to_remove)
# remove_duplicates(layer_containing_some_dups)


# if (total_tiffs > 0):
#     print ('-----------------------')
#     print ('Total TIFs: {}'.format(total_tiffs))
#     print ('Total Geof TIFs: {}'.format(georeferenced_tiffs))
#     print ('Outside Domain TIFs: {}'.format(tiffs_outside_domain))
#     print ('Duplicate Tiffs Purged: {}'.format(duplicates_purged))
#     print ('Captured TIFs: {}'.format(captured_tiffs - tiffs_outside_domain - duplicates_purged))
#     print ('Capture Eff: {}'.format(round(captured_tiffs/georeferenced_tiffs * 100, 1)))
# print ('-----------------------')
# print ('Done!')

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

def create_intersection_points_layer(dissolved_road_layer, dissolved_other_layer):
    count = 0
    print ('Making points')
    timer_start = time.time()
    points_of_intersection = QgsVectorLayer("Point?crs=EPSG:102658&index=yes", "result", "memory")
    index = QgsSpatialIndex(dissolved_road_layer.getFeatures())
    # for f in dissolved_road_layer.getFeatures():
    #     index.insertFeature(f)
    for subject_feature in dissolved_road_layer.getFeatures():
        features_close_to_subject_feature = index.intersects(subject_feature.geometry().boundingBox())
        for close_feature in features_close_to_subject_feature:
            if not close_feature.geometry().equals(subject_feature.geometry()):
                if (close_feature.geometry().intersects(subject_feature.geometry())):
                    # print (f[0])
                    # points_of_intersection = f.geometry().intersection(feature.geometry())
                    line_layer_prine = QgsVectorLayer("LineString?crs=EPSG:102658&index=yes", "result1", "memory")
                    line_layer_sub = QgsVectorLayer("LineString?crs=EPSG:102658&index=yes", "result2", "memory")
                    with edit(line_layer_prine):
                        line_layer_prine.dataProvider().addFeature(subject_feature)
                    with edit(line_layer_sub):
                        line_layer_sub.dataProvider().addFeature(f)

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

points_of_intersection = create_intersection_points_layer(result_layer)

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