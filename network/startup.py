from PyQt5 import QtGui
from PyQt5 import QtWidgets
import os, sys, shutil, re

geopackage_name = "RoadDB.gpkg"
map_name = "Offline-Map.qgs"

network_dir = os.path.join("C:", os.sep, "Users", "Will", "Desktop", "GIS", "Network")
local_pkg_dir =  os.path.join(os.path.expanduser("~"), "Documents", "QGIS-Local")

def read_file(file):
    f = open(file, "r")
    content = f.read()
    f.close()

    if content == '':
        result = 0
    else:
        result = float(content)
    return result

def create_or_update_file(file, value):
    f = open(file, "w+")
    f.write(str(value))
    f.close()
    return

def is_newer_package_avialable(local_file, network_file):
    verson_file = re.sub(r"\.\D+", ".ver", local_file)
    if not os.path.exists(verson_file):
        create_or_update_file(verson_file, 0)

    local_date = read_file(verson_file)
    network_file_date = os.path.getmtime(network_file)
    if local_date < network_file_date:
        return True
    else:
        return False

def update_local_verson(local_file, network_file):
    verson_file = re.sub(r"\.\D+", ".ver", local_file)
    network_file_date = os.path.getmtime(network_file)
    create_or_update_file(verson_file, network_file_date)
    return

def update_local(filename):
    network_file = os.path.join(network_dir, filename)
    local_file = os.path.join(local_pkg_dir, filename)


    if os.path.exists(network_file):
        if is_newer_package_avialable(local_file, network_file):
            if filename == map_name:
                reply = QtWidgets.QMessageBox.question(None, "Update?", 'A new verson of the map document was found. Do you wish to update? \nWarning: This will overwrite your local prefrences but give you access to new layers.', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            else:
                reply = QtWidgets.QMessageBox.Yes
            if reply == QtWidgets.QMessageBox.Yes:
                update_local_verson(local_file, network_file)
                try:
                    os.remove(local_file)
                except FileNotFoundError:
                    pass
                except:
                    print('Unable to remove old local file. Please close all other QGIS instances.')
                shutil.copy2(network_file, local_file)
        #else:
            #QtWidgets.QMessageBox.information(None, "INFO", 'You have the newest verson of '+ filename +' already.')
            
    else:
        QtWidgets.QMessageBox.information(None, "INFO", 'Unable to find ' + filename + ' on the network, using local one for now. \nQGIS will check next time you start the program. \nIf this problem persists, please contact Will Carey.')


if not os.path.exists(local_pkg_dir):
    os.mkdir(local_pkg_dir)

update_local(geopackage_name)
update_local(map_name)
