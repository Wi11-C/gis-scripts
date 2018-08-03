import unittest
import env_config

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_increment(self):
        config = env_config.config()
        self.assertEquals(config.geopackage_name, "RoadDB.gpkg")

if __name__ == '__main__':
    unittest.main()