import unittest
import env_config
import tiffs_to_features_helper
import project_limits_helper
import ProjectLoader

class Test_sheet_number(unittest.TestCase):
    def test_sheet_no(self):
        self.assertEquals(tiffs_to_features_helper.get_sheet_no(r'sheet_77'), "77")
    
    def test_sheet_no2(self):
        self.assertEquals(tiffs_to_features_helper.get_sheet_no(r'sheet 777'), "777")

    def test_sheet_no3(self):    
        self.assertEquals(tiffs_to_features_helper.get_sheet_no(r'sheet77'), "77")

class Test_projectLoader(unittest.TestCase):
    def test_name1(self):
        proj = ProjectLoader.ProjectName('Bishoff Rd, Dead End to Jog Rd', '2016085')
        self.assertEquals(proj.corridor, 'Bishoff Rd')
        # self.assertEquals(proj.start, 'Dead End')
        # self.assertEquals(proj.start, 'Jog Rd')

    def test_cleaner(self):
        proj = ProjectLoader.ProjectName('Bishoff rd., Dead End to Jog Rd', '2016085')
        self.assertEquals(proj.corridor, 'Bishoff Rd')

    def test_cleaner2(self):
        proj = ProjectLoader.ProjectName('Bishoff rd N, Dead End to Jog Rd', '2016085')
        self.assertEquals(proj.corridor, 'Bishoff Rd N')
    
    def test_cleaner3(self):
        proj = ProjectLoader.ProjectName('Bishoff_rd, Dead End to Jog Rd', '2016085')
        self.assertEquals(proj.corridor, 'Bishoff Rd')

    def test_cleaner4(self):
        proj = ProjectLoader.ProjectName('Bishoff rd north, Dead End to Jog Rd', '2016085')
        self.assertEquals(proj.corridor, 'Bishoff Rd N')

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_tiff(self):
        self.assertEquals(tiffs_to_features_helper.correct_link(r'sheet\\\7'), r"sheet\\7")

    def test_config(self):
        config = env_config.config()
        self.assertEquals(config.geopackage_name, "RoadDB.gpkg")

if __name__ == '__main__':
    unittest.main()