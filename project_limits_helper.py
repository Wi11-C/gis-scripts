from qgis.core import *

def CountFeatures(layer):
    count = 0
    for fea in layer.getFeatures():
        count += 1
    return count

def SplitLayer(layer, num_parts):
    count = CountFeatures(layer)
    min_records_per_part = floor(count/num_parts)
    arr_out = []
    last_record = 0
    two_layers = processing.run("saga:splitshapeslayerrandomly", {'SHAPES': layer,'PERCENT':50,'EXACT':True,'A':'memory:','B':'C:/Users/wcarey/AppData/Local/Temp/processing_53f0200bb3304c68a19b989eb7bcf0e5/289472d225b7429ab0562b9b77fda4f9/B.shp'})['OUTPUT']
    for i in range(num_parts-1):

        arr_out.append(lyr)
    return