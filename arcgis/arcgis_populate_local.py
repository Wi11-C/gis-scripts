# -*- coding: utf-8 -*-

import os, arcpy, cPickle, glob, datetime, json, hashlib, re

directory = r"C:\Users\wcarey\Desktop\GIS\NEWDB\\"
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
	
def update_hash(layer, is_feature, dict):
	txt_now = unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	if is_feature:
		check_path = directory + layer.name + ".*"
	else:
		check_path = directory + layer.name.replace(".", "_", 1) + '.*'
	files = glob.glob(check_path)
	
	if files:
		print "computing hash for files..."
		dict[layer.name]["hash"][txt_now] = {}
		for f in files:
			head, tail = os.path.split(f)
			dict[layer.name]["hash"][txt_now][tail] = file_hash(f)
		print "hashing complete"

dictionary = read_file()
mxd = arcpy.mapping.MapDocument(r"C:\Users\wcarey\Desktop\GIS\Data.mxd")
veclayers = [lyr for lyr in arcpy.mapping.ListLayers(mxd) if lyr.isFeatureLayer]
tables = [table for table in arcpy.mapping.ListTableViews(mxd)]
print '********FEATURES********'
get_and_update(veclayers, True, dictionary)
print '********TABLES********'
get_and_update(tables, False, dictionary)
del mxd
