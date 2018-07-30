# -*- coding: utf-8 -*-

from qgis.core import *
#from PyQt4 import *
import qgis.utils, processing, os, shutil

# supply path to qgis install location
#QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.0", True)

# create a reference to the QgsApplication, setting the
# second argument to False disables the GUI
#qgs = QgsApplication([], False)

# load providers
#qgs.initQgis()

#project = QgsProject.instance()
#project.read(QFileInfo(r'C:\Users\wcarey\Desktop\GIS\MakePackageMap.qgs'))
#print (project.fileName())
local_geopackage = os.path.join("C:", os.sep, "Users", "wcarey", "Desktop", "GIS", "RoadDB.gpkg")

if os.path.exists(local_geopackage):
	print ('Removing old Local Geopackage')
	os.remove(local_geopackage)

print ('Making Geopackage')
processing.run("native:package", { 'LAYERS' : ['C:/Users/wcarey/Desktop/GIS/NEWDB/ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NULL AND \"RESP_AUTH\" NOT LIKE \'FDOT\'','C:/Users/wcarey/Desktop/GIS/NEWDB/ENG.CENTERLINE.shp|layerid=0|subset=\"TFARE_ROW\" IS NOT NULL OR \"RESP_AUTH\" = \'FDOT\'','C:/Users/wcarey/Desktop/GIS/NEWDB/ENG.RIGHT_OF_WAY.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/ENG.ROAD_PROJECTS.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/ENG.SIGNAL_PTS_MULTI.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/ENG.TIM_FUTURE_TFARE_LINE.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/Export_LWDD.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/ORTHO_GRID_PY.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/PAO.PARCELS.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/PAO.SUBDIVISIONS.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/PZB_LU_APP_DATA.dbf','C:/Users/wcarey/Desktop/GIS/NEWDB/PZB.LU_APP.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/PZB.ZONING_APPS_PENDING.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/WUD_LG.ASBUILT_PY.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/WUD.RPRESSURIZEDMAIN.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/WUD.SSGRAVITYMAIN.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/WUD.SSMANHOLE.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/WUD.SSPRESSURIZEDMAIN.shp','C:/Users/wcarey/Desktop/GIS/NEWDB/WUD.WPRESSURIZEDMAIN.shp','crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.pbcgov.org/arcgis/rest/services/Ags/3/MapServer/0\' table=\"\" sql=', 'crs=\'EPSG:3857\' filter=\'\' url=\'http://maps.co.palm-beach.fl.us/arcgis/rest/services/Ags/3/MapServer/6\' table=\"\" sql='], 'OUTPUT' : 'C:/Users/wcarey/Desktop/GIS/RoadDB.gpkg', 'OVERWRITE' : False })

print ('Making Township-Section map layer')
processing.run("qgis:dissolve", { 'FIELD' : ['RNGTWN'], 'INPUT' : 'C:/Users/wcarey/Desktop/GIS/NEWDB/ORTHO_GRID_PY.shp', 'OUTPUT' : 'ogr:dbname="C:/Users/wcarey/Desktop/GIS/RoadDB.gpkg" table="RANGE-TOWNSHIP" (geom) sql=' })
#processing.runalg('qgis:dissolve', 'C:/Users/wcarey/Desktop/GIS/NEWDB/ORTHO_GRID_PY.shp', , field, 'ogr:dbname="C:/Users/wcarey/Desktop/GIS/RoadDB.gpkg" table="RANGE-TOWNSHIP" (geom) sql=')

print ('Local Geopackage updated')

network_dir = os.path.join("F:", os.sep, "ROADWAY", "WCarey", "GIS")
network_geopackage = os.path.join(network_dir, "RoadDB.gpkg")

if os.path.exists(network_geopackage):
	print ('Removing old Geopackage from network')
	os.remove(network_geopackage)
print ('Copying Geopackage to network')
shutil.copy2(local_geopackage, network_geopackage)

print ('Done')

#qgs.exitQgis()
