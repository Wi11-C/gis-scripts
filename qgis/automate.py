import os, sys, shutil
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
# from PyQt5.QtCore import *

# Provide constants
local_gis_working_dir = os.path.join("C:", os.sep, "Users", "Will", "Desktop", "GIS")
local_shape_dir = os.path.join(local_gis_working_dir, "NEWDB")
geopackage_name = "RoadDB.gpkg"
local_geopackage_path = os.path.join(local_gis_working_dir, geopackage_name)
network_dir = os.path.join("F:", os.sep, "ROADWAY", "WCarey", "GIS")
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
app = QgsApplication([], True)
QgsApplication.initQgis()

project = QgsProject.instance()
# Load another project
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


if os.path.exists(local_geopackage_path):
	print ('Removing old Local Geopackage')
	os.remove(local_geopackage_path)

print('Loading layers')
# lay = QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.RIGHT_OF_WAY.shp'), 'ENG.RIGHT_OF_WAY', 'ogr')
# local = QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\''), 'Local Roads', 'ogr')
# tfare = QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\''), 'Throughfare Roads', 'ogr')
# commission_districts = QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql=', 'Commdist', 'arcgisfeatureserver')
# epermits = QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 'ePermits', 'arcgisfeatureserver')
Layers_to_package = [
    QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.RIGHT_OF_WAY.shp'), 'ENG.RIGHT_OF_WAY', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.ROAD_PROJECTS.shp'), 'ENG.ROAD_PROJECTS', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.SIGNAL_PTS_MULTI.shp'), 'ENG.SIGNAL_PTS_MULTI', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.TIM_FUTURE_TFARE_LINE.shp'), 'ENG.TIM_FUTURE_TFARE_LINE', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'Export_LWDD.shp'), 'LWDD', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'ORTHO_GRID_PY.shp'), 'ROW Roll Maps', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'PAO.PARCELS.shp'), 'PAO.PARCELS', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'PAO.SUBDIVISIONS.shp'), 'PAO.SUBDIVISIONS', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'PZB_LU_APP_DATA.shp'), 'PZB_LU_APP_DATA', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'PZB.LU_APP.shp'), 'PZB.LU_APP', 'ogr'),

    QgsVectorLayer(os.path.join(local_shape_dir, 'PZB.ZONING_APPS_PENDING.shp'), 'PZB.ZONING_APPS_PENDING', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'WUD_LG.ASBUILT_PY.shp'), 'WUD_LG.ASBUILT_PY', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.RPRESSURIZEDMAIN.shp'), 'WUD.RPRESSURIZEDMAIN', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.SSGRAVITYMAIN.shp'), 'WUD.SSGRAVITYMAIN', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.SSMANHOLE.shp'), 'WUD.SSMANHOLE', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.SSPRESSURIZEDMAIN.shp'), 'WUD.SSPRESSURIZEDMAIN', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'WUD.WPRESSURIZEDMAIN.shp'), 'WUD.WPRESSURIZEDMAIN', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\''), 'Local Roads', 'ogr'),
    QgsVectorLayer(os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\''), 'Throughfare Roads', 'ogr'),
    QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql=', 'Commission Districts', 'arcgisfeatureserver'),
    QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 'ePermits', 'arcgisfeatureserver')

    # os.path.join(local_shape_dir, 'ENG.RIGHT_OF_WAY.shp'),
    # os.path.join(local_shape_dir, 'ENG.ROAD_PROJECTS.shp'),
    # os.path.join(local_shape_dir, 'ENG.SIGNAL_PTS_MULTI.shp'),
    # os.path.join(local_shape_dir, 'ENG.TIM_FUTURE_TFARE_LINE.shp'),
    # os.path.join(local_shape_dir, 'Export_LWDD.shp'),
    # os.path.join(local_shape_dir, 'ORTHO_GRID_PY.shp'),
    # os.path.join(local_shape_dir, 'PAO.PARCELS.shp'),
    # os.path.join(local_shape_dir, 'PAO.SUBDIVISIONS.shp'),
    # os.path.join(local_shape_dir, 'PZB_LU_APP_DATA.dbf'),
    # os.path.join(local_shape_dir, 'PZB.LU_APP.shp'),
    # os.path.join(local_shape_dir, 'PZB.ZONING_APPS_PENDING.shp'),
    # os.path.join(local_shape_dir, 'WUD_LG.ASBUILT_PY.shp'),
    # os.path.join(local_shape_dir, 'WUD.RPRESSURIZEDMAIN.shp'),
    # os.path.join(local_shape_dir, 'WUD.SSGRAVITYMAIN.shp'),
    # os.path.join(local_shape_dir, 'WUD.SSMANHOLE.shp'),
    # os.path.join(local_shape_dir, 'WUD.SSPRESSURIZEDMAIN.shp'),
    # os.path.join(local_shape_dir, 'WUD.WPRESSURIZEDMAIN.shp'),
    # local, 
    # tfare,
    # commission_districts
    # epermits
    # os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\''),
    # os.path.join(local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\''),
    # 'crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql='
    # 'crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 
    ]


Make_geopackage(Layers_to_package)
Add_township_section_to_geopackage()
# PushToNetwork()
print ('Done!')
