__author__ = 'sgibbes'
import os
import arcpy
import datetime
from forestloss_classes import analysistext
from forestloss_classes import remap
from forestloss_classes import jointables
from forestloss_classes import check_duplicates as check
from forestloss_classes import unique_id
from forestloss_classes import directories as dir
from forestloss_classes import analysis
from forestloss_classes import user_inputs
from forestloss_classes import biomass_calcs
from forestloss_classes import boundary_prep
from forestloss_classes import merge_tables

# get user inputs
maindir, input_shapefile, column_name, filename, threshold, forest_loss, carbon_emissions, tree_cover_extent, \
biomass_weight, summarize_by, summarize_file, summarize_by_columnname, overwrite, mosaic_location, admin_location = user_inputs.user_inputs_tool()

# write inputs to text file
analysistext.analysisinfo(maindir, input_shapefile, filename, column_name, threshold, forest_loss, carbon_emissions,
    tree_cover_extent, biomass_weight, summarize_by, summarize_file, summarize_by_columnname, mosaic_location)

# set up file paths, ignore files that aren't needed
option_list = []
# option_list = forest_loss, tree_cover_extent, emissions, biomassweight

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
    shapefile, admin_column_name = boundary_prep.boundary_prep(input_shapefile, summarize_by, adm0, adm1, adm2, maindir,
                                                               filename, summarize_by_columnname, summarize_file)
else:
    shapefile = input_shapefile
    admin_column_name = column_name

total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))

start = datetime.datetime.now()

# remap tcd mosaic based on user input
remapfunction = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remap_functions",
                             'remap_gt' + threshold + '.rft.xml')
loss_tcd_function = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loss_tcd.rft.xml")
remap.remapmosaic(mosaic_location, forest_loss, biomass_weight, remapfunction, loss_tcd_function)

with arcpy.da.SearchCursor(shapefile, ("Shape@", "FC_NAME", column_name)) as cursor:
    feature_count = 0
    for row in cursor:
        fctime = datetime.datetime.now()
        feature_count += 1
        arcpy.AddMessage("processing feature {} out of {}".format(feature_count, total_features))
        fc_geo = row[0]
        column_name2 = row[1]
        orig_fcname = row[2]
        # removed the overwrite option for now
        if forest_loss == "true" and carbon_emissions == "false":
            option_list.append("forest_loss")
            lossyr = os.path.join(mosaic_location, 'loss')
            tcdmosaic = os.path.join(mosaic_location, 'tcd')
            hansenareamosaic = os.path.join(mosaic_location, 'area')
            analysis.forest_loss_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname)

        if tree_cover_extent == "true":
            option_list.append("tree_cover_extent")
            hansenareamosaic = os.path.join(mosaic_location, 'area')
            tcdmosaic = os.path.join(mosaic_location, 'tcd')
            analysis.tree_cover_extent_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,tcdmosaic,filename,orig_fcname)

        if carbon_emissions == "true":
            option_list.extend(["emissions", "forest_loss"])
            lossyr = os.path.join(mosaic_location, 'loss')
            hansenareamosaic = os.path.join(mosaic_location, 'area')
            emissions_mosaic = os.path.join(mosaic_location, 'emissions')
            analysis.carbon_emissions_function(hansenareamosaic, emissions_mosaic, fc_geo,
                                               scratch_gdb, maindir, shapefile, column_name2,
                                               outdir, lossyr, filename, orig_fcname)

        if biomass_weight == "true":
            option_list.append("biomassweight")
            biomassmosaic = os.path.join(mosaic_location, 'biomass')
            hansenareamosaic = os.path.join(mosaic_location, 'area')
            tcdmosaic = os.path.join(mosaic_location, 'tcd')
            analysis.biomass_weight_function(hansenareamosaic, biomassmosaic, fc_geo, scratch_gdb, maindir,
                                             shapefile, column_name2, outdir, tcdmosaic, filename, orig_fcname)


        arcpy.AddMessage("     " + str(datetime.datetime.now() - fctime))

    del cursor

# merge output fc tables into 1 per analysis
arcpy.AddMessage("merge tables")

for option in option_list:
    merge_tables.merge_tables(outdir, option, filename, merged_dir, threshold)

# if "biomass" in option_list:
#     arcpy.AddMessage("calculating carbon emissions")
#     biomass_calcs.calcbiomass(merged_dir, filename)

# if "biomassweight" in option_list:
#     biomassweight = arcpy.ListTables(filename + "_biomassweight")[0]
#     arcpy.AddMessage("calculating biomass density")
#     biomass_calcs.biomass30m_calcs(merged_dir, filename)

jointables.main(merged_dir, filename)

def deletefields(table, fields_to_delete):
    for f in fields_to_delete:
        arcpy.DeleteField_management(table, f)

if carbon_emissions == "true" or forest_loss == "true":
    # deletefields(os.path.join(merged_dir, filename + "_forest_loss"),
    #              ["Value", "COUNT", "AREA", "uID", "L", "S", "SUM"])
    arcpy.TableToTable_conversion(os.path.join(merged_dir, filename + "_forest_loss"), maindir,
                                  filename + "_forest_loss.dbf")
else:
    if tree_cover_extent == "true" and forest_loss == "false":
        arcpy.TableToTable_conversion(os.path.join(merged_dir, filename + "_tree_cover_extent"), maindir,
                                      filename + "_tree_cover_extent.dbf")
    if biomass_weight == "true" and forest_loss == "false":
        # deletefields(os.path.join(merged_dir, filename + "_biomassweight"), ["Value", "AREA", "uID", "L", "S", "SUM"])
        arcpy.TableToTable_conversion(os.path.join(merged_dir, filename + "_biomassweight"), maindir,
                                      filename + "_biomassweight.dbf")
