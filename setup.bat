IF "%PYQGIS_STARTUP%"=="" (
    SET PYQGIS_STARTUP="%APPDATA%\QGIS\QGIS3\profiles\default\python\startup.py"
) ELSE (
    ECHO env var already set
)

xcopy /y %~dp0startup.py "%APPDATA%\QGIS\QGIS3\profiles\default\python"
