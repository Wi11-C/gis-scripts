# -*- coding: utf-8 -*-

import os, arcpy, cPickle, glob, datetime, json, hashlib, re

directory = r"C:\Users\wcarey\Desktop\uploadtest\\"
test_gpkg = 'test2.gpkg'
json_file_path = directory + "DB.txt"

def read_file():
	if os.path.isfile(json_file_path):
		with open(json_file_path, 'r') as file:
			dict = json.load(file)
			return dict
	else:
		print 'Unable to find local DB...making new one'
		return {}
	
def save_file(dict):
	with open(json_file_path, 'w') as file:
		json.dump( dict, file, indent=4)
	print 'json saved'
	return
	
def remove_old_local_file(local_files):
	print 'Removing old local files'
	for f in local_files:
		os.remove(f)
	return
	
def findField(feature, field_name_to_find):
	fieldnames = [field.name for field in arcpy.ListFields(feature.dataSource)]
	if field_name_to_find in fieldnames:
		return True
	else:
		return False
	
def save_local_shape(layer):
	check_path = directory + layer.name + ".*"
	files = glob.glob(check_path)
	if files:
		remove_old_local_file(files)
	else:
		print 'unable to find existing shape file...downloading new one'
	file_path_out = directory + layer.name + ".shp"
	print "Downloading Features..."
	arcpy.CopyFeatures_management(layer.dataSource, file_path_out)
	print "Download Complete"
	return
	
def save_local_table(table):
	file_name = table.name.replace(".", "_", 1)
	file_path_out = directory + file_name + '.*'
	files = glob.glob(file_path_out)
	if files:
		remove_old_local_file(files)
	else:
		print 'unable to find existing table locally...downloading new one'
	print "Downloading table..."
	arcpy.TableToDBASE_conversion(table.dataSource, directory)
	print "Download Complete"
	print ('Correcting File Names')
	correct_table_file_names(table)
	print "Rename Complete"
	return

# When this program is run from the command line, the table prefixes are lost in the function 'TableToDBASE'..so we need to add them back afterwards
def correct_table_file_names(table):
	parts = table.name.split('.',1)
	desired_filename_base = directory + parts[0] + '_' + parts[1]
	local_files = glob.glob(directory + parts[1] + '.*')
	for f_path_and_name in local_files:
		suffix_matches = re.search(r'\.(\w+)$', f_path_and_name)
		suffix = suffix_matches.group(1)
		os.rename(f_path_and_name,desired_filename_base + '.' + suffix)
	return
	
def has_attribute(attribute, data):
    return attribute in data and data[attribute] is not None

def file_hash(filename):
	h = hashlib.sha256()
	with open(filename, 'rb', buffering=0) as f:
		for b in iter(lambda : f.read(128*1024), b''):
			h.update(b)
	return h.hexdigest()

def get_and_update(arr_layers, is_feature, dict):
	for layer in arr_layers:
		print '--------' + layer.name + '--------'
		
		if not has_attribute(layer.name, dict):
			print "No layer in local DB"
			dict[layer.name] = {}
			dict[layer.name]["last_checked"] = "2000-01-01 00:00:00"
			dict[layer.name]["last_updated"] = "2000-01-01 00:00:00"
			dict[layer.name]["min_hours_between_updates"]= 1
			dict[layer.name]["hash"] = {}
		
		last_checked = datetime.datetime.strptime(dict[layer.name]["last_checked"], "%Y-%m-%d %H:%M:%S")
		datediff = datetime.datetime.now() - last_checked
		interval = datetime.timedelta(hours=dict[layer.name]["min_hours_between_updates"])
		if (datediff > interval):
			dict[layer.name]["last_checked"] = unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			if findField(layer, 'DT_CHG'):
				print "Getting latest record from server"
				rows = [r[0] for r in arcpy.da.SearchCursor(layer.dataSource, ['DT_CHG'], where_clause=('DT_CHG IS NOT NULL'), sql_clause=(None, 'ORDER BY DT_CHG DESC'))]
				if len(rows) > 0:
					last_changed_date = rows[0]
				else:
					print "All DT_CHG fields are NULL"
					last_changed_date = datetime.datetime.now()
			else:
				print "Layer does not have DT_CHG field"
				last_changed_date = datetime.datetime.now()
			
			last_updated = datetime.datetime.strptime(dict[layer.name]["last_updated"], "%Y-%m-%d %H:%M:%S")
			
			print ('server date:' u'{0}'.format(last_changed_date))
			print ('local date:' u'{0}'.format(last_updated))
			
			if last_updated < last_changed_date:
				print 'updates were made, updating local copy'
				dict[layer.name]["last_updated"] =  unicode(last_changed_date.strftime("%Y-%m-%d %H:%M:%S"))
				if is_feature:
					save_local_shape(layer)
				else:
					save_local_table(layer)
				update_hash(layer, is_feature, dict)
				save_file(dict)
			else:
				print ("Skipping because we already have most up to date verson")
		else:
			print "Too Soon to check layer, skipping"
	return

def truncateCoordinates(myGeometry):
	truncated_coords = []
	partnum = 0
	for part in (myGeometry):
		for pnt in myGeometry.getPart(partnum):
			if pnt:
				truncated_coords.append("{:10.4f}".format(pnt.X))
				truncated_coords.append("{:10.4f}".format(pnt.Y))
			else:
				continue
		partnum += 1     
	return truncated_coords

# Place all local records without a seq value into a new layer
def add_new_records(local_layer, SDE_layer, new_records_layer, next_network_seq):
	with local_layer.da.SearchCursor(local_layer.dataSource, ["SHAPE@", "PRO_NO", "SHAPE_ACCU", "PRO_NAME", "DESIGN_PM", "STATUS", "LINK", "PROJECT_SEQ"]) as cursor_local:
		for row_network in cursor_local:
			if not row_network[7]:
				record_to_add = [row_network[0],row_network[1],row_network[2],row_network[3],row_network[4],row_network[5],row_network[6],next_network_seq]
				with arcpy.da.InsertCursor(new_records_layer.dataSource, ["SHAPE@", "PRO_NO", "SHAPE_ACCU", "PRO_NAME", "DESIGN_PM", "STATUS", "LINK", "PROJECT_SEQ"]) as cursor:
					cursor.insertRow(record_to_add)
				next_network_seq += next_network_seq
	return

	
def push_updates_to_SDE_layer(local_layer, SDE_layer):
	# for f in local_layer:
	# if feature_exist_in_SDE(f["fid"]):
	with arcpy.da.SearchCursor(SDE_layer.dataSource, ["OID@", "SHAPE@", "PRO_NO"]) as cursor_network: #TODO: Change to update cursor
		for row_network in cursor_network:
			with arcpy.da.SearchCursor(local_layer.dataSource, ["OID@", "SHAPE@", "PRO_NO"]) as cursor_local:
				for row_local in cursor_local:
					if row_network[2] == row_local[2]:
						print "Proj: {}".format(row_network[2])
						geo_network = truncateCoordinates(row_network[1])
						geo_local = truncateCoordinates(row_local[1])
						if geo_network != geo_local:
							print 'Geometries are equal'
							with arcpy.da.InsertCursor(local_layer.dataSource, ["OID@", "SHAPE@", "PRO_NO", "SHAPE_ACCU", "PRO_NAME", "DESIGN_PM", "STATUS", "LINK", "PROJECT_SEQ"]) as cursor_insert:
								
						break
			# print "id: {} shape: {}".format(row[0], row[1])
	return

# def update_hash(layer, is_feature, dict):
# 	txt_now = unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
# 	if is_feature:
# 		check_path = directory + layer.name + ".*"
# 	else:
# 		check_path = directory + layer.name.replace(".", "_", 1) + '.*'
# 	files = glob.glob(check_path)
	
# 	if files:
# 		print "computing hash for files..."
# 		dict[layer.name]["hash"][txt_now] = {}
# 		for f in files:
# 			head, tail = os.path.split(f)
# 			dict[layer.name]["hash"][txt_now][tail] = file_hash(f)
# 		print "hashing complete"

# arcpy.env.workspace = r"C:\Users\wcarey\Desktop\uploadtest"
local_file= r"C:\Users\wcarey\Desktop\ProjectsEdit.gpkg\ProjectsEdit"
mxd = arcpy.mapping.MapDocument(r"C:\Users\wcarey\Desktop\GIS\Data.mxd")
temp_layer = arcpy.management.MakeFeatureLayer(local_file, "local_features").getOutput(0)

check_path = directory + '*.gpkg'
files = glob.glob(check_path)
if files:
	remove_old_local_file(files)
arcpy.CreateSQLiteDatabase_management(directory + test_gpkg,'GEOPACKAGE')

spatial_ref = arcpy.SpatialReference(102658)
print (spatial_ref.datumName)
arcpy.CreateFeatureclass_management(directory + test_gpkg, 'changed', 'POLYGON', local_file, 'DISABLED', 'DISABLED', spatial_ref)
arcpy.env.workspace = directory + test_gpkg + '//changed'

for lyr in arcpy.mapping.ListLayers(mxd):
	if lyr.name == "ENG.ROAD_PROJECTS":
		# push_updates_to_SDE_layer(temp_layer, lyr)
		print ('done')
del mxd
