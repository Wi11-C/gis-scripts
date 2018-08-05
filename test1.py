import unittest
import env_config
import tiffs_to_features_helper
from QGIS_import_Proj_TIFFS import get_sheet_no

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_tiff(self):
        self.assertEquals(tiffs_to_features_helper.correct_link(r'sheet\\\7'), r"sheet\\7")
    
    def test_config(self):
        config = env_config.config()
        self.assertEquals(get_sheet_no(r'sheet_77'), "77")
    
    def test_config(self):
        config = env_config.config()
        self.assertEquals(config.geopackage_name, "RoadDB.gpkg")

if __name__ == '__main__':
    unittest.main()