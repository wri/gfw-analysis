import arcpy
import os

def remapmosaic(threshold,mosaic_location,forest_loss,biomass_weight,tcdmosaic,lossyr,remapfunction,loss_tcd_function):

    from forestloss_classes import mosaic_path as mosaic_path
    path = os.path.dirname(os.path.abspath(__file__))
    arcpy.AddMessage("updating raster function paths")
    from forestloss_classes import mosaic_path
    mosaic_path.mosaic_path(loss_tcd_function,mosaic_location,path)
    loss_tcd_function = os.path.join(os.path.dirname(os.path.abspath(__file__)),"loss_tcd2.rft.xml")
    # remove potential existing function

    if forest_loss == "true":
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

    if biomass_weight == "true":
        arcpy.EditRasterFunction_management(
            tcdmosaic30m, "EDIT_MOSAIC_DATASET",
            "REMOVE", remapfunction)

        arcpy.EditRasterFunction_management(
            tcdmosaic30m, "EDIT_MOSAIC_DATASET",
            "INSERT", remapfunction)