__author__ = 'sgibbes'
import os
import arcpy
import datetime
from forestloss_classes import jointables
from forestloss_classes import check_duplicates as check
from forestloss_classes import unique_id as unique_id
from forestloss_classes import directories as dir
from forestloss_classes import analysis as analysis
from forestloss_classes import biomass_calcs as biomass_calcs
from forestloss_classes import merge_tables

def user_inputs():
    maindir = r'D:\Users\sgibbes\glad_alerts\alerts_biomassresample\test2'
    mosaic_location = r'D:\Users\sgibbes\glad_alerts\glad_alerts_rasters\july\mosaics.gdb'
    admin_location = r'H:\gfw_gis_team_data\gadm27_levels.gdb'
    shapefile = r'D:\Users\sgibbes\glad_alerts\alerts_biomassresample\PER3.shp'
    filename = 'resample'
    column_name = 'adm1_id'
    threshold = 25
    forest_loss = "true"
    carbon_emissions = "true"
    tree_cover_extent = "false"
    biomass_weight = "false"
    summarize_by = 'do not summarize by another boundary'
    summarize_file = "#"
    summarize_by_columnname = "#"
    overwrite = "false"

    analysisinfo = os.path.join(maindir, "analysisinfo.txt")
    if os.path.exists(analysisinfo):
        os.remove(analysisinfo)
    text = open(analysisinfo, 'w')
    text.write("shapefile: {}".format(shapefile)
               + "\nfile name: {}".format(filename)
               + "\ncolumn_name: {}".format(column_name)
               + "\nthreshold: {}".format(threshold)
               + "\nforest_loss: {}".format(forest_loss)
               + "\ncarbon emissions: {}".format(carbon_emissions)
               + "\ntree cover extent: {}".format(tree_cover_extent)
               + "\nbiomass weight: {}".format(biomass_weight)
               + "\nsummarize by: {}".format(summarize_by)
               + "\nsummarize file: {}".format(summarize_file)
               + "\nsummarize by columnname: {}".format(summarize_by_columnname))
    text.close()
    return maindir, shapefile, column_name, filename, threshold, forest_loss, carbon_emissions, tree_cover_extent, \
           biomass_weight, summarize_by, summarize_file, summarize_by_columnname, overwrite, mosaic_location, \
           admin_location


maindir, input_shapefile, column_name, filename, threshold, forest_loss, carbon_emissions, tree_cover_extent, \
biomass_weight, summarize_by, summarize_file, summarize_by_columnname, overwrite, mosaic_location, admin_location = user_inputs()

# set up file paths, ignore files that aren't needed
if forest_loss == "true":
    lossyr = os.path.join(mosaic_location, 'loss')
    tcdmosaic = os.path.join(mosaic_location, 'tcd')
    hansenareamosaic = os.path.join(mosaic_location, 'area')
if tree_cover_extent == "true":
    hansenareamosaic = os.path.join(mosaic_location, 'area')
    tcdmosaic = os.path.join(mosaic_location, 'tcd')
if carbon_emissions == "true":
    biomassmosaic = os.path.join(mosaic_location, 'carbon')
if biomass_weight == "true":
    tcdmosaic30m = os.path.join(mosaic_location, 'tcd_30m')
    hansenareamosaic30m = os.path.join(mosaic_location, 'area_30m')
    biomassmosaic = os.path.join(mosaic_location, 'carbon')

adm0 = os.path.join(admin_location, 'adm0')
adm1 = os.path.join(admin_location, 'adm1')
adm2 = os.path.join(admin_location, 'adm2')

# set up directories
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984")
arcpy.env.workspace = maindir
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

scratch_gdb, outdir, merged_dir = dir.dirs(maindir)

check.check_dups(input_shapefile, column_name)
unique_id.unique_id(input_shapefile, column_name)

# prep boundary if necessary
if summarize_by != "do not summarize by another boundary":
    arcpy.AddMessage('Intersecting with {} boundary'.format(summarize_by))
    from forestloss_classes import boundary_prep as boundary_prep

    shapefile, admin_column_name = boundary_prep.boundary_prep(input_shapefile, summarize_by, adm0, adm1, adm2, maindir,
                                                               filename, summarize_by_columnname, summarize_file)

else:
    shapefile = input_shapefile
    admin_column_name = column_name
total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))

start = datetime.datetime.now()

option_list = []
if forest_loss == "true":
    option_list.append("forest_loss")
if carbon_emissions == "true":
    option_list.extend(["biomass_max", "biomass_min", "biomass"])
if tree_cover_extent == "true":
    option_list.append("tree_cover_extent")
if biomass_weight == "true":
    option_list.extend(["biomass30m", "biomassweight"])

with arcpy.da.SearchCursor(shapefile, ("Shape@", "FC_NAME", column_name)) as cursor:
    feature_count = 0
    for row in cursor:
        fctime = datetime.datetime.now()
        feature_count += 1

        arcpy.AddMessage("processing feature {} out of {}".format(feature_count, total_features))
        fc_geo = row[0]
        column_name2 = row[1]
        orig_fcname = row[2]
        arcpy.AddMessage("processing feature {}".format(column_name2))
        if overwrite == "true":
            if forest_loss == "true" and carbon_emissions == "false":
                analysis.forest_loss_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname)
            if carbon_emissions == "true":
                # forest_loss_function()
                analysis.carbon_emissions_function(hansenareamosaic,biomassmosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname)
            if biomass_weight == "true":
                analysis.biomass_weight_function(hansenareamosaic30m,biomassmosaic,fc_geo,tcdmosaic30m,filename,scratch_gdb,outdir,column_name2,orig_fcname)
            if tree_cover_extent == "true":
                analysis.tree_cover_extent_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,tcdmosaic,filename,orig_fcname)
        if overwrite == "false":
            if forest_loss == "true" and carbon_emissions == "false":
                z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "forest_loss")
                if arcpy.Exists(z_stats_tbl):
                    arcpy.AddMessage("already exists")
                else:
                    analysis.forest_loss_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname)
            if carbon_emissions == "true":
                if column_name2[:3] == "IDN":
                    arcpy.AddMessage("using idn loss yr mosaic")
                    lossyr = os.path.join(mosaic_location, 'loss_idn')
                else:
                    lossyr = os.path.join(mosaic_location, 'loss')

                z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "biomass")
                if arcpy.Exists(z_stats_tbl):
                    arcpy.AddMessage("already exists")
                else:
                    analysis.carbon_emissions_function(hansenareamosaic,biomassmosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname)
            if biomass_weight == "true":
                z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "biomassweight")
                if arcpy.Exists(z_stats_tbl):
                    arcpy.AddMessage("already exists")
                else:
                    analysis.biomass_weight_function()
            if tree_cover_extent == "true":
                z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "tree_cover_extent")
                if arcpy.Exists(z_stats_tbl):
                    arcpy.AddMessage("already exists")
                else:
                    analysis.tree_cover_extent_function()
        arcpy.AddMessage("     " + str(datetime.datetime.now() - fctime))
    del cursor

# merge output fc tables into 1 per analysis


arcpy.AddMessage("merge tables")
for option in option_list:
    merge_tables.merge_tables(outdir, option, filename, merged_dir, threshold)

if "biomass_max" in option_list:
    arcpy.AddMessage("calculating carbon emissions")
    biomass_calcs.avgbiomass(merged_dir, filename)

# if "biomass" in option_list:
#     arcpy.AddMessage("calculating carbon emissions")
#     biomass_calcs.avgbiomass(merged_dir, filename)

if "biomassweight" in option_list:
    biomassweight = arcpy.ListTables(filename + "_biomassweight")[0]
    arcpy.AddMessage("calculating biomass density")
    biomass_calcs.biomass30m_calcs(merged_dir, filename)

jointables.main(merged_dir, filename)


def deletefields(table, fields_to_delete):
    for f in fields_to_delete:
        arcpy.DeleteField_management(table, f)


if carbon_emissions == "true" or forest_loss == "true":
    # deletefields(os.path.join(merged_dir, filename + "_forest_loss"),
    #              ["Value", "AREA", "uID", "L", "S", "SUM"])

    arcpy.TableToTable_conversion(os.path.join(merged_dir, filename + "_forest_loss"), maindir,
                                  filename + "_forest_loss.dbf")
else:
    if tree_cover_extent == "true" and forest_loss == "false":
        arcpy.TableToTable_conversion(os.path.join(merged_dir, filename + "_tree_cover_extent"), maindir,
                                      filename + "_tree_cover_extent.dbf")
    if biomass_weight == "true" and forest_loss == "false":
        deletefields(os.path.join(merged_dir, filename + "_biomassweight"), ["Value", "AREA", "uID", "L", "S", "SUM"])
        arcpy.TableToTable_conversion(os.path.join(merged_dir, filename + "_biomassweight"), maindir,
                                      filename + "_biomassweight.dbf")
