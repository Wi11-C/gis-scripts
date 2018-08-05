import unittest
import env_config
from tiffs_to_features_helper import *
from project_limits_helper import *

class Test_sheet_number(unittest.TestCase):
    def test_sheet_no(self):
        self.assertEquals(get_sheet_no(r'sheet_77'), "77")
    
    def test_sheet_no2(self):
        self.assertEquals(get_sheet_no(r'sheet 777'), "777")

    def test_sheet_no3(self):    
        self.assertEquals(get_sheet_no(r'sheet77'), "77")

# class Test_import_helper(unittest.TestCase):
#     def test_count(self):
#         layer1=

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_tiff(self):
        self.assertEquals(correct_link(r'sheet\\\7'), r"sheet\\7")

    def test_config(self):
        config = env_config.config()
        self.assertEquals(config.geopackage_name, "RoadDB.gpkg")

if __name__ == '__main__':
    unittest.main()