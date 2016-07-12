import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

def forest_loss_function(snap,fcgeo,zoneraster):
    arcpy.env.snapRaster =snap
    tcdmosaic = r'C:\Users\samantha.gibbes\Documents\gis\sample_tiles\mosaics.gdb\tcd'
    print "extracting {} with geo {}".format(zoneraster,fcgeo)
    lossyr_tcd = ExtractByMask(zoneraster,fcgeo) + tcdmosaic
    return lossyr_tcd

def carbon_emissions_function(snap,fcgeo,zoneraster):
    arcpy.env.snapRaster = snap
    tcdmosaic = r'C:\Users\samantha.gibbes\Documents\gis\sample_tiles\mosaics.gdb\tcd'

    lossyr_tcd = ExtractByMask(zoneraster, fc_geo)+tcdmosaic
    return lossyr_tcd
def biomass_weight():
    arcpy.env.snapRaster = hansenareamosaic30m
    biomassweight = ExtractByMask(biomassmosaic,fc_geo)*(Raster(hansenareamosaic30m)/10000)
    return biomassweight
def biomass_area():
    arcpy.env.snapRaster = hansenareamosaic30m
    area30m = ExtractByMask(hansenareamosaic30m,fc_geo)
    return area30m
def tree_cover_extent_function():
    arcpy.env.snapRaster = hansenareamosaic
    tcd_extract = ExtractByMask(tcdmosaic, fc_geo)
    return tcd_extract