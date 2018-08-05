from qgis.core import *

def CountFeatures(layer):
    count = 0
    for fea in layer.getFeatures():
        count += 1
    return count