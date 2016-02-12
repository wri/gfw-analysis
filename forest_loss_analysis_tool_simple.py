__author__ = 'sgibbes'
import os
import arcpy
from arcpy import *
from arcpy.sa import *
import time, subprocess
from sys import argv
from boundary_prep_arcpro import *
from dictionaries import dict
def remapmosaic(threshold,remaptable):
    tcdcolumn = "tcd"+str(threshold)
    rows = arcpy.UpdateCursor(remaptable)
    for row in rows:
        output = row.getValue(tcdcolumn)
        row.output = output
        rows.updateRow(row)
    del rows
    arcpy.EditRasterFunction_management(
     tcdmosaic, "EDIT_MOSAIC_DATASET",
     "REPLACE", remapfunction)
def zonal_stats_forest(zone_raster, value_raster, filename, calculation, snapraster):
    arcpy.AddMessage(  "zonal stats")
    arcpy.env.snapRaster = snapraster
    if calculation == "biomass_max" or calculation == "area"or calculation == "area_only":
        arcpy.env.cellSize = "MAXOF"
    if calculation == "biomass_min":
        arcpy.env.cellSize = "MINOF"
    if calculation == "area_30m" or calculation == "biomass_30m":
        arcpy.env.cellSize = "MAXOF"
    expr = fc_name.split("_")[0]

    z_stats_tbl = os.path.join(outdir, fc_name + "_" + filename + "_" + calculation)

    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + expr + "'", "PYTHON_9.3")
    if not calculation in option_list:
        option_list.append(calculation)

def merge_tables(envir,option,filename,merged_dir):
    arcpy.env.workspace = envir
    table_list = arcpy.ListTables("*_"+option)
    arcpy.AddMessage(table_list)
    final_merge_table = os.path.join(merged_dir,filename+"_"+option + "_merge")
    arcpy.AddMessage(final_merge_table)
    arcpy.Merge_management(table_list,final_merge_table)
    # delete rows where valye <15 and add Year field and update rows
    dict = {15:"no loss",16:"y2001",17:"y2002",18:"y2003",19:"y2004",20:"y2005",21:"y2006",22:"y2007",23:"y2008",24:"y2009",25:"y2010",26:"y2011",27:"y2012",28:"y2013",29:"y2014"}
    arcpy.AddField_management(final_merge_table,"Year","TEXT","","",10)
    with arcpy.da.UpdateCursor(final_merge_table, ["Value","Year"]) as cursor:
        for row in cursor:
            if row[0] < 15:
                cursor.deleteRow()
            for v in range(15,30):
                if row[0] == v:
                    row[1] = dict[v]
                    cursor.updateRow(row)
        del cursor
# average the min/max biomass tables
def avgBiomass(merged_dir,userinput_columnname):
    arcpy.env.workspace = merged_dir
    area = arcpy.ListTables("*_area_merge")[0]
    max = arcpy.ListTables("*_max_merge")[0]
    min = arcpy.ListTables("*_min_merge")[0]

    arcpy.AddField_management(max,"L","DOUBLE")
    arcpy.AddField_management(max,"uID","TEXT")
    userinput_columnname = "Name_1"
    "'" + userinput_columnname + "'"
    arcpy.CalculateField_management(max,"L","!SUM!", "PYTHON_9.3", "")
    arcpy.CalculateField_management(max,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")
    expression = """ !ID! +"_"+str( !Value!)"""
    arcpy.CalculateField_management(max,"uID",expression, "PYTHON_9.3", "")
    arcpy.DeleteField_management(max,"SUM")

    arcpy.AddField_management(min,"S","DOUBLE")
    arcpy.AddField_management(min,"uID","TEXT")
    arcpy.CalculateField_management(min,"S","!SUM!", "PYTHON_9.3", "")
    arcpy.CalculateField_management(min,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")
    arcpy.DeleteField_management(min,"SUM")

    arcpy.AddField_management(area,"uID","TEXT")
    arcpy.CalculateField_management(area,"uID","""!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.JoinField_management(area,"uID",max,"uID",["L"])
    arcpy.JoinField_management(area,"uID",min,"uID",["S"])
    arcpy.AddField_management(area,"avgBiomass","DOUBLE")
    arcpy.CalculateField_management(area,"avgBiomass","(( !SUM!/10000)/ !COUNT! * ( !L!/1000000)+( !SUM!/10000)/ !COUNT! * ( !S!/1000000))/2", "PYTHON_9.3", "")
def pivotTable(input_table,field,fname):
    pivottable = os.path.join(merged_dir,fname)
    arcpy.management.PivotTable(input_table, "ID", "Year", field, pivottable)

    # add total field
    arcpy.AddField_management(pivottable, "total", "DOUBLE")
    fc = pivottable
    # making a list of fields for the year columns, excluse year 0
    field_prefix = "y"
    field_list = []
    f_list = arcpy.ListFields(fc)
    for f in f_list:
        if field_prefix in f.name:
            field_list.append(f.name)
    # use update cursor to find values and update the total field
    rows = arcpy.UpdateCursor(fc)
    for row in rows:
        total = 0
        for f in field_list:
            total += row.getValue(f)
        row.total = total
        rows.updateRow(row)
        del total
    del rows
def loss_and_biomass(option):
    arcpy.env.scratchWorkspace = scratch_gdb
    table_names_27m = ["area","biomass_max","biomass_min"]
    z_stats_tbl = os.path.join(outdir, fc_name + "_" + filename + "_" + table_names_27m[0])
    if option != "None":
        if not os.path.exists(z_stats_tbl):
            arcpy.env.snapRaster = hansenareamosaic
            arcpy.AddMessage(  "extracting")
            lossyr_tcd = ExtractByMask(lossyearmosaic,fc_geo) + Raster(tcdmosaic)
            try:
                if option == "loss":
                    table = table_names_27m[0]
                    zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename,table,hansenareamosaic)
                    if not table in option_list:
                        option_list.append(table)
                if option == "loss and biomass":
                    zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename,table_names_27m[0],hansenareamosaic)
                    zonal_stats_forest(lossyr_tcd, biomassmosaic, filename,table_names_27m[1],hansenareamosaic)
                    zonal_stats_forest(lossyr_tcd, biomassmosaic, filename,table_names_27m[2],hansenareamosaic)
                    if not table_names_27m[0] in option_list:
                        option_list.extend(table_names_27m)

                del lossyr_tcd
            except IOError as e:
                arcpy.AddMessage(  "     failed")
                error_text = "I/O error({0}): {1}".format(e.errno, e.strerror)
                errortext = open(error_text_file,'a')
                errortext.write(fc_name + " " + str(error_text) + "\n")
                errortext.close()
                pass
            except ValueError:
                arcpy.AddMessage(  "     failed")
                error_text="Could not convert data to an integer."
                errortext = open(error_text_file,'a')
                errortext.write(fc_name + " " + str(error_text) + "\n")
                errortext.close()
                pass
            except:
                arcpy.AddMessage(  "     failed")
                error_text= "Unexpected error:", sys.exc_info()
                error_text= error_text[1][1]
                errortext = open(error_text_file,'a')
                errortext.write(fc_name + " " + str(error_text) + "\n")
                errortext.close()
                pass

        else:
            arcpy.AddMessage(  "already exists")
    else:
        arcpy.AddMessage(  "passing")
        pass

    return option_list
def biomass30m(option):

    if option == "biomass":
        # prepare value and zone raster for 30m data
        arcpy.env.snapRaster = hansenareamosaic30m
        arcpy.env.cellSize = "MAXOF"

        arcpy.AddMessage(  "extracting biomass")
        # prepare value and zone raster for 30m data
        outExtractbyMask = ExtractByMask(biomassmosaic,fc_geo)
        area_extract = ExtractByMask(hansenareamosaic30m,fc_geo)
        outPlus =outExtractbyMask*(Raster(hansenareamosaic30m)/10000)

        # send data to zonal stats function
        zonal_stats_forest(tcdmosaic30m, area_extract, filename, "area30m",hansenareamosaic30m)
        zonal_stats_forest(tcdmosaic30m, outPlus, filename, "biomass30m",hansenareamosaic30m)
        if not "area30m" in option_list:
            option_list.extend(["area30m","biomass30m"])
        time = str(datetime.datetime.now() - start)
    if option == "none":
        pass
    return option_list
def user_inputs():
    maindir = arcpy.GetParameterAsText(0)
    shapefile = arcpy.GetParameterAsText(1)
    filename = GetParameterAsText(2)
    column_name=arcpy.GetParameterAsText(3)
    main_analysis= arcpy.GetParameterAsText(4)
    biomass_analysis = arcpy.GetParameterAsText(5)
    if main_analysis == "area only":
        input_zone = arcpy.GetParameterAsText(6)
    threshold = arcpy.GetParameterAsText(7)
    return maindir, shapefile,column_name,main_analysis,biomass_analysis,filename,threshold
#--------------------------
def inputfile():
    # set input files
    hansenareamosaic = r'H:\gfw_gis_team_data\mosaics.gdb\hansen_area'
    biomassmosaic = r'H:\gfw_gis_team_data\whrc_carbon\whrc_carbon.gdb\whrc_carbon'
    tcdmosaic30m = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_30m_2000'
    hansenareamosaic30m = r'H:\gfw_gis_team_data\mosaics.gdb\hansen_area_30m'
    lossyearmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\lossdata_2001_2014'
    tcdmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_2000'
    # tcdmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_2010'
    adm0 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm0'
    adm1 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm1'
    adm2 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm2'
    grid = r'H:\gfw_gis_team_data\lossdata_footprint.shp'
# set input files
hansenareamosaic = arcpy.GetParameterAsText(8)
biomassmosaic = arcpy.GetParameterAsText(9)
tcdmosaic30m = arcpy.GetParameterAsText(10)
hansenareamosaic30m = arcpy.GetParameterAsText(11)
lossyearmosaic = arcpy.GetParameterAsText(12)
tcdmosaic = arcpy.GetParameterAsText(13)
remaptable = arcpy.GetParameterAsText(14)
remapfunction = arcpy.GetParameterAsText(15)
# get user inputs
maindir, shapefile, column_name,main_analysis,biomass_analysis,filename,threshold = user_inputs()

# remap tcd mosaic based on user input
remapmosaic(threshold,remaptable)

# set up directories
arcpy.env.workspace = maindir
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"
scratch_gdb = os.path.join(maindir, "scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir, "scratch.gdb")
arcpy.env.scratchWorkspace = scratch_gdb
error_text_file = os.path.join(maindir,'errors.txt')
outdir = os.path.join(maindir, "outdir.gdb")
if not os.path.exists(outdir):
    arcpy.CreateFileGDB_management(maindir, "outdir.gdb")

merged_dir = os.path.join(maindir, "merged.gdb")
if not os.path.exists(merged_dir):
    arcpy.CreateFileGDB_management(maindir, "merged.gdb")
# get feature count, set up to start looping
total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))
start = datetime.datetime.now()
option_list = []
arcpy.AddMessage(column_name )
with arcpy.da.SearchCursor(shapefile, ("Shape@", column_name)) as cursor:
    feature_count = 0
    for row in cursor:
        fctime = datetime.datetime.now()
        feature_count += 1
        fc_geo = row[0]
        fc_name = str(row[1])
        arcpy.AddMessage( fc_name + " " + str(feature_count)+"/"+str(total_features))
        loss_and_biomass(main_analysis)
        biomass30m(biomass_analysis)
        arcpy.AddMessage(option_list)
        arcpy.AddMessage(  "     " + str(datetime.datetime.now() - fctime))
    del cursor

# merge output fc tables into 1 per analysis
arcpy.AddMessage(  "merge tables")
for option in option_list:
    merge_tables(outdir,option,filename,merged_dir)

if "area" in option_list:
    arcpy.env.workspace = merged_dir
    area = arcpy.ListTables("*_area_merge")[0]
    arcpy.AddMessage(  "create loss pivot")
    pivotTable(area,"SUM","area_pivot")
if "biomass_max" in option_list:
    arcpy.AddMessage(  "calc average biomass")
    avgBiomass(merged_dir)
    arcpy.AddMessage(  "create biomass pivot")
    pivotTable(area,"avgBiomass","biomass_pivot")
    arcpy.AddMessage(  "\n total elapsed time: " + str(datetime.datetime.now() - start))
