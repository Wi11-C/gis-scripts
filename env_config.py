import os

class config:
    def __init__(self):
        if os.getlogin() == 'Will': # Dev computer
            self.env = 'DEV'
            network_directory = os.path.join("C:", os.sep, "Users", os.getlogin(), "Desktop", "GIS", "Network")
        else: # Run computer
            network_directory = os.path.join("F:", os.sep, "ROADWAY", "WCarey", "GIS")
            self.env = 'PROD'
        self.local_gis_working_dir = os.path.join("C:", os.sep, "Users", os.getlogin(), "Desktop", "GIS")
        self.local_shape_dir = os.path.join(self.local_gis_working_dir, "NEWDB")
        self.geopackage_name = "RoadDB.gpkg"
        self.local_geopackage_path = os.path.join(self.local_gis_working_dir, self.geopackage_name)
        self.network_dir = network_directory
        self.network_geopackage_path = os.path.join(self.network_dir, self.geopackage_name)