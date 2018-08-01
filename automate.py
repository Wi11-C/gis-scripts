import os, sys, shutil, env_config
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms

config = env_config.config()

def PushToNetwork():
    print ('Pushing Geopackage to network')
    if os.path.exists(config.network_geopackage_path):
        print ('Removing old Geopackage from network')
        os.remove(config.network_geopackage_path)
    print ('Copying Geopackage to network')
    shutil.copy2(config.local_geopackage_path, config.network_geopackage_path)
    return

def Make_geopackage(Arr_layers):
    print ('Making Geopackage')
    feedback = QgsProcessingFeedback()
    processing.run("native:package", { 'LAYERS' : Layers_to_package, 'OUTPUT' : config.local_geopackage_path, 'OVERWRITE' : True }, feedback=feedback)
    return

def Add_township_section_to_geopackage():
    print ('Making Township-Section map layer')
    params = {
        'FIELD': ['RNGTWN'],
        'INPUT' : os.path.join(config.local_shape_dir, 'ORTHO_GRID_PY.shp'),
        'OUTPUT' : 'ogr:dbname="' + config.local_geopackage_path + '" table="RANGE-TOWNSHIP" (geom) sql='
    }
    processing.run("qgis:dissolve", params)
    print ('Local Geopackage updated')
    return
	
def Create_KML():
    road_project_layer = QgsVectorLayer(os.path.join(config.local_shape_dir, 'ENG.ROAD_PROJECTS.shp'), 'ENG.ROAD_PROJECTS', 'ogr')
    road_project_layer.setSubsetString('"STATUS" LIKE \'DESIGN\' OR "STATUS" LIKE \'CONSTRUCTION\'')
    network_kml_path = os.path.join(config.network_dir, "Roadway_projects")
    QgsVectorFileWriter.writeAsVectorFormat(road_project_layer, network_kml_path, "utf-8", road_project_layer.crs(), "KML")
    return

QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.2", True)
app = QgsApplication([], True)
QgsApplication.initQgis()

project = QgsProject.instance()
project.read(os.path.join(config.local_gis_working_dir, 'MakePackageMap.qgs'))

sys.path.append(r'C:\Program Files\QGIS 3.2\apps\qgis\python\plugins')
from processing.core.Processing import Processing
Processing.initialize()
import processing
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

if os.path.exists(config.local_geopackage_path):
	print ('Removing old Local Geopackage')
	os.remove(config.local_geopackage_path)
	
Layers_to_package = [
	os.path.join(config.local_shape_dir, 'ENG.RIGHT_OF_WAY.shp'),
    os.path.join(config.local_shape_dir, 'ENG.ROAD_PROJECTS.shp'),
    os.path.join(config.local_shape_dir, 'ENG.SIGNAL_PTS_MULTI.shp'),
    os.path.join(config.local_shape_dir, 'ENG.TIM_FUTURE_TFARE_LINE.shp'),
    os.path.join(config.local_shape_dir, 'Export_LWDD.shp'),
    os.path.join(config.local_shape_dir, 'ORTHO_GRID_PY.shp'),
    os.path.join(config.local_shape_dir, 'PAO.PARCELS.shp'),
    os.path.join(config.local_shape_dir, 'PAO.SUBDIVISIONS.shp'),
    os.path.join(config.local_shape_dir, 'PZB_LU_APP_DATA.dbf'),
    os.path.join(config.local_shape_dir, 'PZB.LU_APP.shp'),
    os.path.join(config.local_shape_dir, 'PZB.ZONING_APPS_PENDING.shp'),
    os.path.join(config.local_shape_dir, 'WUD_LG.ASBUILT_PY.shp'),
    os.path.join(config.local_shape_dir, 'WUD.RPRESSURIZEDMAIN.shp'),
    os.path.join(config.local_shape_dir, 'WUD.SSGRAVITYMAIN.shp'),
    os.path.join(config.local_shape_dir, 'WUD.SSMANHOLE.shp'),
    os.path.join(config.local_shape_dir, 'WUD.SSPRESSURIZEDMAIN.shp'),
    os.path.join(config.local_shape_dir, 'WUD.WPRESSURIZEDMAIN.shp'),
    QgsVectorLayer(os.path.join(config.local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\''), 'Local Roads', 'ogr'),
    QgsVectorLayer(os.path.join(config.local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\''), 'Throughfare Roads', 'ogr'),
    QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql=', 'County Commission Districts', 'arcgisfeatureserver')
    ]

# Since we don't have epermits at home, remvove the layer to avoid error
if config.env == "PROD":
    Layers_to_package.append(
        QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 'ePermits', 'arcgisfeatureserver')
        )

Make_geopackage(Layers_to_package)
Add_township_section_to_geopackage()
PushToNetwork()
Create_KML()

print ('Done!')
sys.exit()
