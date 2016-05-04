__author__ = 'sgibbes'
import os
import arcpy
from arcpy import *
from arcpy.sa import *
import time, subprocess
from sys import argv
from boundary_prep_arcpro import *
from dictionaries import dict

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
    arcpy.AddMessage(remapfunction)
    arcpy.EditRasterFunction_management(
     tcdmosaic, "EDIT_MOSAIC_DATASET",
     "INSERT", remapfunction)

    arcpy.EditRasterFunction_management(
     tcdmosaic30m, "EDIT_MOSAIC_DATASET",
     "INSERT", remapfunction)
def biomass30m_calcs(merged_dir,column_name,filename):
    arcpy.env.workspace = merged_dir
    area30 = arcpy.ListTables("*"+filename+"_area30m")[0]
    biomass30 = arcpy.ListTables("*"+filename+"_biomass30m")[0]
    arcpy.AddMessage(biomass30)
    arcpy.AddMessage(" add field bio30m to biomass")
    arcpy.AddField_management(biomass30,"bio30m","DOUBLE")
    arcpy.CalculateField_management(biomass30,"bio30m","!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(biomass30,"SUM")

    column_name = "!"+column_name+"!"
    arcpy.AddField_management(biomass30,"uID","TEXT")
    arcpy.CalculateField_management(biomass30,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(area30,"uID","TEXT")
    arcpy.CalculateField_management(area30,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.JoinField_management(area30,"uID",biomass30,"uID",["bio30m"])
    arcpy.AddField_management(area30,"Mgha30m","DOUBLE")
    arcpy.AddMessage("calculating mgha30m")
    arcpy.CalculateField_management(area30,"Mgha30m","!bio30m!/(!SUM!/10000)", "PYTHON_9.3", "")
def avgBiomass(merged_dir,column_name,filename):
    # average the min/max biomass tables
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
    arcpy.AddField_management(area,"avgBiomass","DOUBLE")
    arcpy.CalculateField_management(area,"avgBiomass","((!SUM!/10000)/!COUNT! * (!L!/1000000)+ (!SUM!/10000)/!COUNT! * ( !S!/1000000)/2)*.5*3.67", "PYTHON_9.3", "")
def zonal_stats_forest(zone_raster, value_raster, filename, calculation, snapraster,column_name):
    arcpy.AddMessage(  "zonal stats")
    arcpy.env.snapRaster = snapraster
    if calculation == "biomass_max" or calculation == "forest_loss"or calculation == "area_only":
        arcpy.env.cellSize = "MAXOF"
    if calculation == "biomass_min":
        arcpy.env.cellSize = "MINOF"
    if calculation == "area_30m" or calculation == "biomass_30m":
        arcpy.env.cellSize = "MAXOF"

    # if " " in column_name:
    #     column_name = column_name.replace(" ","_")
    # if column_name[0].isdigit():
    #     column_name = "x"+str(column_name)

    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + calculation)

    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    # add a field to identify the table onces it is merged with the other zonal stats tables
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + column_name + "'", "PYTHON_9.3")
    if not calculation in option_list:
        option_list.append(calculation)
def merge_tables(outdir,option,filename,merged_dir):
    arcpy.env.workspace = outdir
    table_list = arcpy.ListTables("*"+filename+"_"+option)
    arcpy.AddMessage(table_list)
    final_merge_table = os.path.join(merged_dir,filename+"_"+option)
    arcpy.Merge_management(table_list,final_merge_table)
    if option == "area30m" or option ==  "area only":
        arcpy.AddMessage("dictionary only to 20")
        dict =  {20:"value"}
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
    tcd_year_table = r'D:\Users\sgibbes\regular_script_test\2001_2019_tcd_year_codes.dbf'
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
        arcpy.CalculateField_management(final_merge_table, "tcd", threshold, "PYTHON_9.3", "")

def forest_loss_function():
    arcpy.AddMessage("extracting for forest loss")
    lossyr_tcd = ExtractByMask(lossyearmosaic, fc_geo) + Raster(tcdmosaic)
    calculation = "forest_loss"
    zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename, calculation, hansenareamosaic, column_name)
    if not calculation in option_list:
        option_list.append(calculation)
    del lossyr_tcd
def carbon_emissions_function():
    arcpy.AddMessage("extracting for carbon emissions")
    lossyr_tcd = ExtractByMask(lossyearmosaic, fc_geo) + Raster(tcdmosaic)
    zonal_stats_forest(lossyr_tcd, biomassmosaic, filename, "biomass_max", hansenareamosaic, column_name)
    zonal_stats_forest(lossyr_tcd, biomassmosaic, filename, "biomass_min", hansenareamosaic, column_name)
    if not "biomass_max" in option_list:
        option_list.extend("biomass_max")
    del lossyr_tcd
def biomass_weight_function():
    arcpy.env.snapRaster = hansenareamosaic30m
    arcpy.env.cellSize = "MAXOF"
    arcpy.AddMessage("extracting for biomass weight")
    outExtractbyMask = ExtractByMask(biomassmosaic,fc_geo)
    area_extract = ExtractByMask(hansenareamosaic30m,fc_geo)
    outPlus =outExtractbyMask*(Raster(hansenareamosaic30m)/10000)

    # send data to zonal stats function
    zonal_stats_forest(tcdmosaic30m, area_extract, filename, "area30m", hansenareamosaic30m, column_name)
    zonal_stats_forest(tcdmosaic30m, outPlus, filename, "biomass30m", hansenareamosaic30m, column_name)
    if not "area30m" in option_list:
        option_list.extend(["area30m", "biomass30m"])
    time = str(datetime.datetime.now() - start)
def tree_cover_extent_function():
    arcpy.AddMessage("extracting for tree cover extent")
    tcd_extract = ExtractByMask(tcdmosaic, fc_geo)
    zonal_stats_forest(tcd_extract, hansenareamosaic, filename, "tree_cover_extent", hansenareamosaic, column_name)
    if not "tree_cover_extent" in option_list:
        option_list.extend("tree_cover_extent")
    del tcd_extract
def analysis(function_input):
    arcpy.env.scratchWorkspace = scratch_gdb
    table_names_27m = ["area","biomass_max","biomass_min","area_only"]
    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + table_names_27m[0])
    if not os.path.exists(z_stats_tbl):
        arcpy.env.snapRaster = hansenareamosaic
        try:
            if option == "forest loss":
                arcpy.AddMessage(  "extracting for forest loss")
                lossyr_tcd = ExtractByMask(lossyearmosaic,fc_geo) + Raster(tcdmosaic)
                table = table_names_27m[0]
                zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename,table,hansenareamosaic,column_name)
                if not table in option_list:
                    option_list.append(table)
                del lossyr_tcd
            if option == "carbon emissions":
                arcpy.AddMessage(  "extracting for carbon emissions")
                lossyr_tcd = ExtractByMask(lossyearmosaic,fc_geo) + Raster(tcdmosaic)
                zonal_stats_forest(lossyr_tcd, biomassmosaic, filename,table_names_27m[1],hansenareamosaic,column_name)
                zonal_stats_forest(lossyr_tcd, biomassmosaic, filename,table_names_27m[2],hansenareamosaic,column_name)
                if not table_names_27m[0] in option_list:
                    option_list.extend(table_names_27m)
                del lossyr_tcd
            if option == "tree cover extent":
                arcpy.AddMessage(  "extracting for tree cover extent")
                tcd_extract = ExtractByMask(tcdmosaic,fc_geo)
                zonal_stats_forest(tcd_extract, hansenareamosaic, filename,table_names_27m[3],hansenareamosaic,column_name)
                if not table_names_27m[3] in option_list:
                    option_list.extend(table_names_27m)
                del tcd_extract
            if option == "biomass weight":
                # prepare value and zone raster for 30m data
                arcpy.env.snapRaster = hansenareamosaic30m
                arcpy.env.cellSize = "MAXOF"
                arcpy.AddMessage("extracting for biomass weight")
                outExtractbyMask = ExtractByMask(biomassmosaic, fc_geo)
                area_extract = ExtractByMask(hansenareamosaic30m, fc_geo)
                outPlus = outExtractbyMask * (Raster(hansenareamosaic30m) / 10000)
                # send data to zonal stats function
                zonal_stats_forest(tcdmosaic30m, area_extract, area_type, "area30m", hansenareamosaic30m)
                zonal_stats_forest(tcdmosaic30m, outPlus, area_type, "biomass30m", hansenareamosaic30m)
                if not "area30m" in option_list:
                    option_list.extend(["area30m", "biomass30m"])
                return option_list
        except IOError as e:
            arcpy.AddMessage(  "     failed")
            error_text = "I/O error({0}): {1}".format(e.errno, e.strerror)
            errortext = open(error_text_file,'a')
            errortext.write(column_name + " " + str(error_text) + "\n")
            errortext.close()
            pass
        except ValueError:
            arcpy.AddMessage(  "     failed")
            error_text="Could not convert data to an integer."
            errortext = open(error_text_file,'a')
            errortext.write(column_name + " " + str(error_text) + "\n")
            errortext.close()
            pass
        except:
            arcpy.AddMessage(  "     failed")
            error_text= "Unexpected error:", sys.exc_info()
            error_text= error_text[1][1]
            errortext = open(error_text_file,'a')
            errortext.write(column_name + " " + str(error_text) + "\n")
            errortext.close()
            pass
    else:
        arcpy.AddMessage(  "already exists")
    return option_list
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

    return maindir, shapefile, column_name,filename, threshold,forest_loss,carbon_emissions,tree_cover_extent,biomass_weight
#--------------------------
# set input files
hansenareamosaic = r'D:\Users\sgibbes\simpe_script_test\mosaics.gdb\area'
biomassmosaic = r'D:\Users\sgibbes\simpe_script_test\mosaics.gdb\biomass'
tcdmosaic30m = r'D:\Users\sgibbes\simpe_script_test\mosaics.gdb\tcd_30m'
hansenareamosaic30m = r'D:\Users\sgibbes\simpe_script_test\mosaics.gdb\area_30m'
lossyearmosaic = r'D:\Users\sgibbes\simpe_script_test\mosaics.gdb\loss_year'
tcdmosaic = r'D:\Users\sgibbes\simpe_script_test\mosaics.gdb\tcd'
# tcdmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_2010'
adm0 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm0'
adm1 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm1'
adm2 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm2'
grid = r'H:\gfw_gis_team_data\lossdata_footprint.shp'

remaptable = os.path.join(os.path.dirname(os.path.abspath(__file__)),"remaptable.dbf")
remapfunction = os.path.join(os.path.dirname(os.path.abspath(__file__)),"remapfunction.rft.xml")
arcpy.AddMessage(remapfunction)
# get user inputs
maindir, shapefile, column_name,filename,threshold,forest_loss,carbon_emissions,tree_cover_extent, biomass_weight = user_inputs()

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

# get feature count, set up to start looping
total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))
start = datetime.datetime.now()
option_list = []


def correctfcname(column_name):
    # column_name = unicode(column_name,"ascii","ignore")
    if column_name[0].isdigit():
        column_name = "x"+str(column_name)
    bad = [" ","-",'/', ':', '*', '?', '"', '<', '>', '|','.']
    for char in bad:
        column_name = column_name.replace(char,"_")
    return  column_name

with arcpy.da.SearchCursor(shapefile, ("Shape@", column_name)) as cursor:
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
        # skip loss and biomass if area file exists
        # table_names = {"area only":"area_only","loss and biomass":"area","biomass":"biomass30m","loss":"area"}
        # analysisfilename = function.split("()")[0]
        # z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + analysisfilename)
        # arcpy.AddMessage(z_stats_tbl)
        if forest_loss == "true":
            z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_forest_loss")
            forest_loss_function()
        if carbon_emissions == "true":
            carbon_emissions_function()
        if biomass_weight == "true":
            biomass_weight_function()
        if tree_cover_extent == "true":
            tree_cover_extent_function()

        #
        # if overwrite == "true":
        #     analysis(analysis_choice)

        arcpy.AddMessage(  "     " + str(datetime.datetime.now() - fctime))
    del cursor

arcpy.AddMessage(option_list)
# merge output fc tables into 1 per analysis
arcpy.AddMessage(  "merge tables")
for option in option_list:
    merge_tables(outdir,option,filename,merged_dir)

# if area was calculated, create area pivot table
# if biomass max exists, then need to average biomass then create biomass pivot table
arcpy.env.workspace = merged_dir
# area = arcpy.ListTables(filename+"_forest_loss_merge")
# if len(area)==1:
#     area = arcpy.ListTables(filename+"forest_loss")[0]
#     arcpy.AddMessage(  "create loss pivot")
#     pivotTable(area,"SUM",filename + "forest_loss")
if "biomass_max" in option_list:
    arcpy.AddMessage(  "calc average biomass")
    avgBiomass(merged_dir,column_name,filename)
    # arcpy.AddMessage(  "create biomass pivot")
    # pivotTable(area,"avgBiomass",filename + "_biomass_pivot")

if "area30m" in option_list:
    area30m = arcpy.ListTables(filename+"_area30m")[0]
    arcpy.AddMessage(  "calc average 30m biomass")
    biomass30m_calcs(merged_dir,column_name,filename)
    # arcpy.AddMessage(  "create 30m biomass pivot")
    # pivotTable(area30m,"Mgha30m",filename + "_biomass30m_pivot")
    # pivotTable(area30m,"SUM",filename + "_area30m_pivot")

# if "area_only" in option_list:
#     areaonly =arcpy.ListTables(filename+"_area_only_merge")[0]
#     arcpy.AddMessage(  "create area only pivot")
#     pivotTable(areaonly,"SUM",filename + "_area_only_pivot")

# clean up temp files
# arcpy.AddMessage("cleaning up temps")
# arcpy.env.workspace = merged_dir
# temp = arcpy.ListTables("*merge")
# for t in temp:
#     arcpy.Delete_management(t)
# arcpy.Delete_management(outdir)
# arcpy.Delete_management(scratch_gdb)
