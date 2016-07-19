import arcpy
import os
def user_inputs_tool():
    shapefile = arcpy.GetParameterAsText(0)
    maindir = arcpy.GetParameterAsText(1)
    mosaic_location = arcpy.GetParameterAsText(2)


    filename = arcpy.GetParameterAsText(3)
    column_name = arcpy.GetParameterAsText(4)
    threshold = arcpy.GetParameterAsText(5)
    forest_loss = arcpy.GetParameterAsText(6)
    carbon_emissions = arcpy.GetParameterAsText(7)
    tree_cover_extent = arcpy.GetParameterAsText(8)
    biomass_weight = arcpy.GetParameterAsText(9)
    summarize_by = arcpy.GetParameterAsText(10)
    admin_location = arcpy.GetParameterAsText(11)
    summarize_file = arcpy.GetParameterAsText(12)
    summarize_by_columnname = arcpy.GetParameterAsText(13)
    overwrite = arcpy.GetParameterAsText(14)

    return maindir, shapefile, column_name, filename, threshold, forest_loss, carbon_emissions, tree_cover_extent, \
           biomass_weight, summarize_by, summarize_file, summarize_by_columnname, overwrite, mosaic_location, \
           admin_location

def user_inputs_manual():
    maindir = r'D:\Users\sgibbes\forest_carbon_emissions\compare_carbon'
    mosaic_location = r'D:\Users\sgibbes\forest_carbon_emissions\mosaics.gdb'
    admin_location = r'H:\gfw_gis_team_data\gadm27_levels.gdb'
    shapefile = r'D:\Users\sgibbes\forest_carbon_emissions\idn34.shp'
    filename = 'newcarbon'
    column_name = 'OBJECTID'
    threshold = "30"
    forest_loss = "true"
    carbon_emissions = "true"
    tree_cover_extent = "false"
    biomass_weight = "false"
    summarize_by = 'do not summarize by another boundary'
    summarize_file = "#"
    summarize_by_columnname = "#"
    overwrite = "false"


    return maindir, shapefile, column_name, filename, threshold, forest_loss, carbon_emissions, tree_cover_extent, \
           biomass_weight, summarize_by, summarize_file, summarize_by_columnname, overwrite, mosaic_location, \
           admin_location