import os

import arcpy

from raster_functions import mosaic_path


def remapmosaic(mosaic_location,forest_loss,biomass_weight,remapfunction,loss_tcd_function):

    path = os.path.dirname(os.path.abspath(__file__))
    arcpy.AddMessage("updating raster function paths")
    mosaic_path.mosaic_path(loss_tcd_function, mosaic_location, path)
    loss_tcd_function = os.path.join(os.path.dirname(os.path.abspath(__file__)),"loss_tcd2.rft.xml")
    # remove potential existing function
    tcdmosaic = os.path.join(mosaic_location, 'tcd')
    lossyr = os.path.join(mosaic_location, 'loss')


    arcpy.AddMessage("removing existing raster functions")
    arcpy.EditRasterFunction_management(
    tcdmosaic, "EDIT_MOSAIC_DATASET",
    "REMOVE", remapfunction)

    arcpy.EditRasterFunction_management(
        lossyr, "EDIT_MOSAIC_DATASET",
        "REMOVE", remapfunction)

    arcpy.AddMessage("inserting functions")
    arcpy.EditRasterFunction_management(
        tcdmosaic, "EDIT_MOSAIC_DATASET",
        "INSERT", remapfunction)

    arcpy.EditRasterFunction_management(
      lossyr, "EDIT_MOSAIC_DATASET",
     "INSERT", loss_tcd_function)

    # if biomass_weight == "true":
    #     arcpy.EditRasterFunction_management(
    #         tcdmosaic30m, "EDIT_MOSAIC_DATASET",
    #         "REMOVE", remapfunction)
    #
    #     arcpy.EditRasterFunction_management(
    #         tcdmosaic30m, "EDIT_MOSAIC_DATASET",
    #         "INSERT", remapfunction)