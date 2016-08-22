__author__ = 'sgibbes'
import os
import arcpy
from arcpy import *
from arcpy.sa import *
import time, subprocess
from sys import argv

from dictionaries_v2 import dict

def remapmosaic(threshold,remaptable,remapfunction):
    arcpy.AddMessage("removing potential existing function from tcd 27m")
    # remove potential existing function
    arcpy.EditRasterFunction_management(
    tcdmosaic, "EDIT_MOSAIC_DATASET",
    "REMOVE", remapfunction)

    arcpy.AddMessage("removing potential existing function from tcd 30m")
    arcpy.EditRasterFunction_management(
    tcdmosaic30m, "EDIT_MOSAIC_DATASET",
    "REMOVE", remapfunction)

    # copying remap values from tcd column into the "output" column for remap table
    tcdcolumn = "tcd"+str(threshold)
    arcpy.AddMessage("updating remap table column")
    rows = arcpy.UpdateCursor(remaptable)
    for row in rows:
        output = row.getValue(tcdcolumn)
        row.output = output
        rows.updateRow(row)
    del rows
    arcpy.EditRasterFunction_management(
     tcdmosaic, "EDIT_MOSAIC_DATASET",
     "INSERT", remapfunction)

    arcpy.EditRasterFunction_management(
     tcdmosaic30m, "EDIT_MOSAIC_DATASET",
     "INSERT", remapfunction)
def zonal_stats_forest(zone_raster, value_raster, filename, calculation, snapraster,column_name):
    arcpy.AddMessage(           "zonal stats")
    arcpy.env.snapRaster = snapraster
    if calculation == "biomass_max" or calculation == "forest_loss"or calculation == "area_only":
        arcpy.env.cellSize = "MAXOF"
    if calculation == "biomass_min":
        arcpy.env.cellSize = "MINOF"
    if calculation == "area_30m" or calculation == "biomass_30m":
        arcpy.env.cellSize = "MAXOF"
    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + calculation)
    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    # add a field to identify the table onces it is merged with the other zonal stats tables
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + column_name + "'", "PYTHON_9.3")
def forest_loss_function():
    arcpy.env.snapRaster = hansenareamosaic
    lossyr_tcd = ExtractByMask(lossyr,fc_geo) + Raster(tcdmosaic)
    zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename, "forest_loss", hansenareamosaic, column_name)
def carbon_emissions_function():
    lossyr_tcd = ExtractByMask(lossyr, fc_geo)+tcdmosaic
    zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename, "forest_loss", hansenareamosaic, column_name)
    zonal_stats_forest(lossyr_tcd, biomassmosaic, filename, "biomass_max", hansenareamosaic, column_name)
    zonal_stats_forest(lossyr_tcd, biomassmosaic, filename, "biomass_min", hansenareamosaic, column_name)
    zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename, "forest_loss", hansenareamosaic, column_name)
    del lossyr_tcd
def biomass_weight_function():
    arcpy.env.snapRaster = hansenareamosaic30m
    arcpy.env.cellSize = "MAXOF"
    arcpy.AddMessage("extracting for biomass weight")
    try:
        outExtractbyMask = ExtractByMask(biomassmosaic,fc_geo)
        area_extract = ExtractByMask(hansenareamosaic30m,fc_geo)
        outPlus =outExtractbyMask*(Raster(hansenareamosaic30m)/10000)
        zonal_stats_forest(tcdmosaic30m, area_extract, filename, "biomassweight", hansenareamosaic30m, column_name)
        zonal_stats_forest(tcdmosaic30m, outPlus, filename, "biomass30m", hansenareamosaic30m, column_name)
    except:
        # arcpy.AddMessage("     failed")
        # error_text = "I/O error({0}): {1}".format(e.errno, e.strerror)
        # errortext = open(error_text_file, 'a')
        # errortext.write(filename + " " + str(error_text) + "\n")
        # errortext.close()
        pass
def tree_cover_extent_function():
    arcpy.AddMessage("extracting for tree cover extent")
    tcd_extract = ExtractByMask(tcdmosaic, fc_geo)
    zonal_stats_forest(tcd_extract, hansenareamosaic, filename, "tree_cover_extent", hansenareamosaic, column_name)
    # if not "tree_cover_extent" in option_list:
    #     option_list.extend("tree_cover_extent")
    del tcd_extract
def merge_tables(outdir,option,filename,merged_dir):
    arcpy.env.workspace = outdir
    table_list = arcpy.ListTables("*"+filename+"_"+option)
    arcpy.AddMessage(table_list)
    final_merge_table = os.path.join(merged_dir,filename+"_"+option)
    arcpy.Merge_management(table_list,final_merge_table)
    if option == "biomassweight" or option ==  "area only":
        dict =  {20:"no loss"}
    else:
        # delete rows where valye <15 and add Year field and update rows
        dict = {20:"no loss",21:"y2001",22:"y2002",23:"y2003",24:"y2004",25:"y2005",26:"y2006",27:"y2007",28:"y2008",29:"y2009",30:"y2010",31:"y2011",32:"y2012",33:"y2013",34:"y2014",35:"y2015",36:"y2016",37:"y2017",38:"y2018",39:"y2019",40:"y2020"}
    arcpy.AddField_management(final_merge_table,"Year","TEXT","","",10)
    with arcpy.da.UpdateCursor(final_merge_table, ["Value","Year"]) as cursor:
        for row in cursor:
            if row[0] < 20:
                cursor.deleteRow()
            for v in range(20,40):
                if row[0] == v:
                    row[1] = dict[v]
                    cursor.updateRow(row)
        del cursor

    # join tcd/year code table to output table and calculate clean year column

    arcpy.JoinField_management(final_merge_table, "Value", tcd_year_table, "f1", ["year","tcd"])

    arcpy.CalculateField_management(final_merge_table,"Year","!year_1!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(final_merge_table, "year_1")
    if option == "forest_loss" or option == "carbon_emissions":
        with arcpy.da.UpdateCursor(final_merge_table, ["Year"]) as cursor:
            for row in cursor:
                if row[0] == "0":
                    row[0]= "no loss"
                    cursor.updateRow(row)
                if len(row[0]) == 1:
                    row[0] = "200" + row[0]
                    cursor.updateRow(row)
                if len(row[0]) == 2:
                    row[0] = "20" + row[0]
                    cursor.updateRow(row)
            del cursor
    else:
        arcpy.DeleteField_management(final_merge_table, "Year")
    if threshold != "all":
        exp =  "> "+str(threshold)
        arcpy.CalculateField_management(final_merge_table, "tcd", '"'+exp+'"', "PYTHON_9.3", "")
    arcpy.AlterField_management(final_merge_table, "SUM", new_field_alias="area_m2")
def avgBiomass(merged_dir,column_name,filename):
    # average the min/max biomass tables
    arcpy.AddMessage("average biomass")
    arcpy.env.workspace = merged_dir
    area = arcpy.ListTables("*"+filename+"_forest_loss")[0]
    max = arcpy.ListTables("*"+filename+"_biomass_max")[0]
    min = arcpy.ListTables("*"+filename+"_biomass_min")[0]

    arcpy.AddField_management(max,"L","DOUBLE")
    arcpy.CalculateField_management(max,"L","!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(max,"SUM")

    arcpy.AddField_management(max,"uID","TEXT")
    arcpy.CalculateField_management(max,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(min,"S","DOUBLE")
    arcpy.CalculateField_management(min,"S","!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(min,"SUM")

    arcpy.AddField_management(min,"uID","TEXT")
    arcpy.CalculateField_management(min,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(area,"uID","TEXT")
    arcpy.CalculateField_management(area,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.JoinField_management(area,"uID",max,"uID",["L"])
    arcpy.JoinField_management(area,"uID",min,"uID",["S"])
    arcpy.AddField_management(area,"Emissions_mtc02","DOUBLE")
    arcpy.CalculateField_management(area,"Emissions_mtc02","((!SUM!/10000)/!COUNT! * (!L!/1000000)+ (!SUM!/10000)/!COUNT! * ( !S!/1000000)/2)*.5*3.67", "PYTHON_9.3", "")
def biomass30m_calcs(merged_dir,column_name,filename):
    arcpy.env.workspace = merged_dir
    area30 = arcpy.ListTables("*"+filename+"_biomassweight")[0]
    biomass30 = arcpy.ListTables("*"+filename+"_biomass30m")[0]
    arcpy.AddField_management(biomass30,"MgBiomass","DOUBLE")
    arcpy.CalculateField_management(biomass30,"MgBiomass","!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(biomass30,"SUM")

    column_name = "!"+column_name+"!"
    arcpy.AddField_management(biomass30,"uID","TEXT")
    arcpy.CalculateField_management(biomass30,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(area30,"uID","TEXT")
    arcpy.CalculateField_management(area30,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.JoinField_management(area30,"uID",biomass30,"uID",["MgBiomass"])
    arcpy.AddField_management(area30,"MgBiomassPerHa","DOUBLE")
    arcpy.AddMessage("calculating MgBiomassPerHa")
    arcpy.CalculateField_management(area30,"MgBiomassPerHa","!MgBiomass!/(!SUM!/10000)", "PYTHON_9.3", "")

    fields_to_delete = ("Value", "COUNT", "AREA", "uID")
    for f in fields_to_delete:
        arcpy.DeleteField_management(area30, f)
    arcpy.Delete_management(biomass30)
def user_inputs():
    maindir = arcpy.GetParameterAsText(0)
    shapefile = arcpy.GetParameterAsText(1)
    filename = arcpy.GetParameterAsText(2)
    column_name = arcpy.GetParameterAsText(3)
    threshold = arcpy.GetParameterAsText(4)
    forest_loss = arcpy.GetParameterAsText(5)
    carbon_emissions = arcpy.GetParameterAsText(6)
    tree_cover_extent = arcpy.GetParameterAsText(7)
    biomass_weight = arcpy.GetParameterAsText(8)
    summarize_by = arcpy.GetParameterAsText(9)
    summarize_file = arcpy.GetParameterAsText(10)
    summarize_by_columnname= arcpy.GetParameterAsText(11)
    overwrite = arcpy.GetParameterAsText(12)
    return maindir, shapefile, column_name,filename, threshold,forest_loss,carbon_emissions,tree_cover_extent,biomass_weight,summarize_by,summarize_file,summarize_by_columnname,overwrite
def boundary_prep(input_shapefile):
    admin_level = summarize_by
    if summarize_by != "choose my own file": # run admin level boundary prep
        admin_column_name, column_calc, area_type, admin_file = dict(admin_level, adm0, adm1, adm2,column_name)
    else: # get user's file and column name
        admin_column_name = "feature_ID" # created this name- generatic
        column_calc = """str( !"""+column_name+"""!)+"___"+str( !"""+summarize_by_columnname+"""!)"""
        admin_file = summarize_file
    shapefile = os.path.join(outdir,filename+"_intersect")
    arcpy.Intersect_analysis([input_shapefile,admin_file],shapefile)
    arcpy.AddField_management(shapefile, admin_column_name, "TEXT", "", "", 50)
    arcpy.CalculateField_management(shapefile, admin_column_name, column_calc, "PYTHON_9.3")

    return shapefile,admin_column_name
def correctfcname(column_name):
    # column_name = unicode(column_name,"ascii","ignore")
    if column_name[0].isdigit():
        column_name = "x"+str(column_name)
    bad = [" ","-",'/', ':', '*', '?', '"', '<', '>', '|','.',"_"]
    for char in bad:
        column_name = column_name.replace(char,"_")
    return  column_name
#--------------------------
# set input files
mosaic_location = r'C:\Users\samantha.gibbes\Documents\gis\sample_tiles\mosaics.gdb'
admin_location = r'C:\Users\samantha.gibbes\Documents\gis\admin_boundaries\gadm27_levels.gdb'
hansenareamosaic = os.path.join(mosaic_location,'area')
biomassmosaic = os.path.join(mosaic_location,'carbon')
tcdmosaic30m = os.path.join(mosaic_location,'tcd_30m')
hansenareamosaic30m = os.path.join(mosaic_location,'area_30m')
lossyr = os.path.join(mosaic_location,'loss')
tcdmosaic = os.path.join(mosaic_location,'tcd')
adm0 = os.path.join(admin_location,'adm0')
adm1 = os.path.join(admin_location,'adm1')
adm2 = os.path.join(admin_location,'adm2')
grid = r'C:\Users\samantha.gibbes\Documents\gis\admin_boundaries\lossdata_footprint.shp'
tcd_year_table = os.path.join(os.path.dirname(os.path.abspath(__file__)),"2001_2019_tcd_year_codes.dbf")
# remap table is located in folder where this script is stored
remaptable = os.path.join(os.path.dirname(os.path.abspath(__file__)),"remaptable.dbf")
remapfunction = os.path.join(os.path.dirname(os.path.abspath(__file__)),"remapfunction.rft.xml")

# get user inputs
maindir, input_shapefile, column_name,filename,threshold,forest_loss,carbon_emissions,tree_cover_extent, biomass_weight, summarize_by,summarize_file,summarize_by_columnname,overwrite= user_inputs()

# remap tcd mosaic based on user input
remapmosaic(threshold,remaptable,remapfunction)

# set up directories
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984")
arcpy.env.workspace = maindir
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

scratch_gdb = os.path.join(maindir, "scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir, "scratch.gdb")
arcpy.env.scratchWorkspace = scratch_gdb
error_text_file = os.path.join(maindir,'errors.txt')
outdir = os.path.join(maindir, "temp.gdb")
if not os.path.exists(outdir):
    arcpy.CreateFileGDB_management(maindir, "temp.gdb")
merged_dir = os.path.join(maindir, "final.gdb")
if not os.path.exists(merged_dir):
    arcpy.CreateFileGDB_management(maindir, "final.gdb")

# prep boundary if necessary
if summarize_by != "do not summarize by another boundary": # if user is summarizing by admin boundary, need to create a new id column based on
    # the intersection of column_name value and iso values
    shapefile,admin_column_name = boundary_prep(input_shapefile)
else:
    shapefile = input_shapefile
    admin_column_name = column_name
total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))
start = datetime.datetime.now()

option_list = []
if forest_loss == "true":
    option_list.append("forest_loss")
if carbon_emissions == "true":
    option_list.extend(["biomass_max", "biomass_min"])
if tree_cover_extent == "true":
    option_list.append("tree_cover_extent")
if biomass_weight == "true":
    option_list.extend(["biomass30m", "biomassweight"])

with arcpy.da.SearchCursor(shapefile, ("Shape@", admin_column_name)) as cursor:
    feature_count = 0
    for row in cursor:
        fctime = datetime.datetime.now()
        feature_count += 1
        fc_geo = row[0]
        c = row[1]
        c2 = c.encode("utf-8","ignore")
        column_name = unicode(c2,"ascii","ignore")
        column_name2 = correctfcname(column_name)
        arcpy.AddMessage(column_name2)
        if column_name2 == "PER7":
            pass
        else:
            if overwrite == "true":
                if forest_loss == "true" and carbon_emissions == "false":
                    forest_loss_function()
                if carbon_emissions == "true":
                    # forest_loss_function()
                    carbon_emissions_function()
                if biomass_weight == "true":
                    biomass_weight_function()
                if tree_cover_extent == "true":
                    tree_cover_extent_function()
            if overwrite == "false":
                if forest_loss == "true" and carbon_emissions == "false":
                    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "forest_loss")
                    if arcpy.Exists(z_stats_tbl):
                        arcpy.AddMessage("already exists")
                    else:
                        forest_loss_function()
                if carbon_emissions == "true":
                    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "biomass_max")
                    if arcpy.Exists(z_stats_tbl):
                        arcpy.AddMessage("already exists")
                    else:
                        carbon_emissions_function()
                if biomass_weight == "true":
                    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "biomass_weight")
                    if arcpy.Exists(z_stats_tbl):
                        arcpy.AddMessage("already exists")
                    else:
                        biomass_weight_function()
                if tree_cover_extent == "true":
                    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "tree_cover_extent")
                    if arcpy.Exists(z_stats_tbl):
                        arcpy.AddMessage("already exists")
                    else:
                        tree_cover_extent_function()

                #     z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "forest_loss")
                #     z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "biomass_max")
                #     z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "biomass_weight")
                #     z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "tree_cover_extent")
                #     if not arcpy.Exists(z_stats_tbl):
                #
                #     else:
                #         arcpy.AddMessage("already exists")
                # if biomass_weight == "true":
                #     z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "biomass_weight")
                #     if arcpy.Exists(z_stats_tbl) and overwrite == "true":
                #         biomass_weight_function()
                #     else:
                #         arcpy.AddMessage("already exists")
                # if tree_cover_extent == "true":
                #     z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + "tree_cover_extent")
                #     if not arcpy.Exists(z_stats_tbl):
                #         tree_cover_extent_function()
            arcpy.AddMessage(  "     " + str(datetime.datetime.now() - fctime))
    del cursor

# merge output fc tables into 1 per analysis
arcpy.AddMessage(  "merge tables")
for option in option_list:
    merge_tables(outdir,option,filename,merged_dir)

arcpy.env.workspace = merged_dir

if "biomass_max" in option_list:
    arcpy.AddMessage(  "calc average biomass")
    avgBiomass(merged_dir,column_name,filename)

if "biomassweight" in option_list:
    biomassweight = arcpy.ListTables(filename+"_biomassweight")[0]
    arcpy.AddMessage(  "calc average 30m biomass")
    biomass30m_calcs(merged_dir,column_name,filename)

# clean up temp files
# arcpy.AddMessage("cleaning up temps")
# arcpy.env.workspace = merged_dir
# temp = arcpy.ListTables("*merge")
# for t in temp:
#     arcpy.Delete_management(t)
# arcpy.Delete_management(outdir)
# arcpy.Delete_management(scratch_gdb)
