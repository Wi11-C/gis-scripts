import os, sys, shutil, env_config
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
from project_limits_helper import CountFeatures

config = env_config.config()
update_SFWMD_now = False

# Functions
def remove_local_package(package_to_remove):
    if os.path.exists(package_to_remove):
        print ('Removing old Local Geopackage')
        os.remove(package_to_remove)
    return

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
    print('Exporting active projects to KML')
    road_project_layer = QgsVectorLayer(os.path.join(config.local_shape_dir, 'ENG.ROAD_PROJECTS.shp'), 'ENG.ROAD_PROJECTS', 'ogr')
    road_project_layer.setSubsetString('"STATUS" LIKE \'DESIGN\' OR "STATUS" LIKE \'CONSTRUCTION\'')
    network_kml_path = os.path.join(config.network_dir, "Roadway_projects")
    QgsVectorFileWriter.writeAsVectorFormat(road_project_layer, network_kml_path, "utf-8", road_project_layer.crs(), "KML")
    return

def Update_SFWMD_layer(layer_path):
    print ('Updating SFWMD Layer....getting latest from server')
    SFWMD_layer = QgsVectorLayer('crs=\'EPSG:3857\' filter=\'NAME is not NULL\' url=\'https://services1.arcgis.com/sDAPyc2rGRn7vf9B/arcgis/rest/services/AHED_Hydroedges/FeatureServer/0\' table=\"\" sql=', 'SFWMD_CANALS', 'arcgisfeatureserver')
    
    print ('Processing SFWMD Layer...deleting features outside county limits')
    SFWMD_local_layer = processing.run("native:clip", {'INPUT':SFWMD_layer,'OVERLAY':'C:/Users/wcarey/Desktop/GIS/NEWDB/countyBoundry.gpkg','OUTPUT':'memory:'})['OUTPUT']

    print ("{} features".format(CountFeatures(SFWMD_local_layer)))
    print ('Processing SFWMD Layer...deleting unnamed features')
    features = SFWMD_local_layer.getFeatures()
    count = 0
    with edit(SFWMD_local_layer):
        for f in features:
            if f['NAME'] == NULL: #qgis.core.NULL
                count += 1
                SFWMD_local_layer.deleteFeature(f.id())
    print ("{} features were null".format(count))
    print ("{} features".format(CountFeatures(SFWMD_local_layer)))
    provider = SFWMD_local_layer.dataProvider()
    QgsVectorFileWriter.writeAsVectorFormat(SFWMD_local_layer, layer_path, provider.encoding(), provider.crs())
    SFWMD_local_layer = None
    # TODO: Clean up to either merge LWDD with SFWMD or connect SFWMD lines that break at roads
    return

def Compile_layers():
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
        os.path.join(config.local_shape_dir, 'old_projects.gpkg'),
        os.path.join(config.local_shape_dir, 'SFWMD_CANALS.gpkg'),
        QgsVectorLayer(os.path.join(config.local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\''), 'Local Roads', 'ogr'),
        QgsVectorLayer(os.path.join(config.local_shape_dir, 'ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\''), 'Throughfare Roads', 'ogr'),
        QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql=', 'County Commission Districts', 'arcgisfeatureserver')
        ]

    # Since we don't have epermits at home, remvove the layer to avoid error
    if config.env == "PROD":
        Layers_to_package.append(
            QgsVectorLayer('crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 'ePermits', 'arcgisfeatureserver')
            )
    return Layers_to_package

# PROJECT SETUP
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.2", True)
app = QgsApplication([], True)
QgsApplication.initQgis()

project = QgsProject.instance()

if update_SFWMD_now:
    remove_local_package(os.path.join(config.local_shape_dir,'SFWMD_CANALS.gpkg'))

project.read(os.path.join(config.local_gis_working_dir, 'MakePackageMap.qgs'))

sys.path.append(r'C:\Program Files\QGIS 3.2\apps\qgis\python\plugins')
from processing.core.Processing import Processing
Processing.initialize()
import processing
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

# PROJECT LOGIC
remove_local_package(config.local_geopackage_path)
if update_SFWMD_now:
    Update_SFWMD_layer(os.path.join(config.local_shape_dir,'SFWMD_CANALS.gpkg'))
Layers_to_package = Compile_layers()  
Make_geopackage(Layers_to_package)
Add_township_section_to_geopackage()
PushToNetwork()
Create_KML()

print ('Done!')
sys.exit()
