:Automation
@echo off
ECHO DOWNLOADING LAYERS

C:\Python27\ArcGIS10.4\python.exe "H:\arcgis_populate_local.py"

ECHO CREATED SHAPE FILES

CALL "C:\Program Files\QGIS 3.2\bin\python-qgis.bat" H:\automate.py

timeout /t -1
