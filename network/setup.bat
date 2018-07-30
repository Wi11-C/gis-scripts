IF "%PYQGIS_STARTUP%"=="" (
    SETX PYQGIS_STARTUP "%APPDATA%\QGIS\QGIS3\profiles\default\python\startup.py"
) ELSE (
    ECHO env var already set
)

xcopy /Y "%~dp0startup.py" "%APPDATA%\QGIS\QGIS3\profiles\default\python\startup.py"

timeout /t -1
