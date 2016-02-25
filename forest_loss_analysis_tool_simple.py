#!/usr/bin/python
# This Python file uses the following encoding: utf-8
import os
import arcpy
from arcpy import *
from arcpy.sa import *
import time, subprocess
from sys import argv
from boundary_prep_arcpro import *
from dictionaries import dict
def remapmosaic(threshold,remaptable,remapfunction):

    if main_analysis != "none":
        arcpy.AddMessage("removing potential existing function from tcd 27m")
        # remove potential existing function
        arcpy.EditRasterFunction_management(
        tcdmosaic, "EDIT_MOSAIC_DATASET",
        "REMOVE", remapfunction)
    if biomass_analysis != "none":
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
    arcpy.AddMessage(  "zonal stats")
    arcpy.env.snapRaster = snapraster
    if calculation == "biomass_max" or calculation == "area"or calculation == "area_only":
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
def biomass30m_calcs(merged_dir,column_name,filename):
    arcpy.env.workspace = merged_dir
    area30 = arcpy.ListTables("*"+filename+"_area30m_merge")[0]
    biomass30 = arcpy.ListTables("*"+filename+"_biomass30m_merge")[0]
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
    arcpy.CalculateField_management(area30,"Mgha30m","!bio30m!/(!SUM!/10000)", "PYTHON_9.3", "")
def merge_tables(outdir,option,filename,merged_dir):
    arcpy.env.workspace = outdir
    table_list = arcpy.ListTables("*"+filename+"_"+option)
    final_merge_table = os.path.join(merged_dir,filename+"_"+option + "_merge")
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
def avgBiomass(merged_dir,column_name,filename):
    # average the min/max biomass tables
    arcpy.env.workspace = merged_dir
    area = arcpy.ListTables("*"+filename+"_area_merge")[0]
    max = arcpy.ListTables("*"+filename+"_biomass_max_merge")[0]
    min = arcpy.ListTables("*"+filename+"_biomass_min_merge")[0]

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
def pivotTable(input_table,field,fname):
    pivottable = os.path.join(merged_dir,fname)
    arcpy.management.PivotTable(input_table, "ID", "Year", field, pivottable)
    # add total field
    fc = pivottable
    # making a list of fields for the year columns, excluse year 0
    arcpy.AddField_management(pivottable, "total", "DOUBLE")
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
    table_names_27m = ["area","biomass_max","biomass_min","area_only"]
    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + table_names_27m[0])
    if not os.path.exists(z_stats_tbl):
        arcpy.env.snapRaster = hansenareamosaic
        try:
            if option == "loss":
                arcpy.AddMessage(  "extracting for loss 27m")
                lossyr_tcd = ExtractByMask(lossyearmosaic,fc_geo) + Raster(tcdmosaic)
                table = table_names_27m[0]
                zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename,table,hansenareamosaic,column_name)
                if not table in option_list:
                    option_list.append(table)
                del lossyr_tcd
            if option == "loss and biomass":
                arcpy.AddMessage(  "extracting for loss and biomass 27m")
                lossyr_tcd = ExtractByMask(lossyearmosaic,fc_geo) + Raster(tcdmosaic)
                zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename,table_names_27m[0],hansenareamosaic,column_name)
                zonal_stats_forest(lossyr_tcd, biomassmosaic, filename,table_names_27m[1],hansenareamosaic,column_name)
                zonal_stats_forest(lossyr_tcd, biomassmosaic, filename,table_names_27m[2],hansenareamosaic,column_name)
                if not table_names_27m[0] in option_list:
                    option_list.extend(table_names_27m)
                del lossyr_tcd
            if option == "area only":
                arcpy.AddMessage(  "extracting for area only")
                tcd_extract = ExtractByMask(tcdmosaic,fc_geo)
                zonal_stats_forest(tcd_extract, hansenareamosaic, filename,table_names_27m[3],hansenareamosaic,column_name)
                if not table_names_27m[3] in option_list:
                    option_list.extend(table_names_27m)
                del tcd_extract
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
        zonal_stats_forest(tcdmosaic30m, area_extract, filename, "area30m",hansenareamosaic30m,column_name)
        zonal_stats_forest(tcdmosaic30m, outPlus, filename, "biomass30m",hansenareamosaic30m,column_name)
        if not "area30m" in option_list:
            option_list.extend(["area30m","biomass30m"])
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
    threshold = arcpy.GetParameterAsText(6)
    return maindir, shapefile,column_name,main_analysis,biomass_analysis,filename,threshold
#--------------------------

# set input files
lossyearmosaic = arcpy.GetParameterAsText(7)
tcdmosaic = arcpy.GetParameterAsText(8)
hansenareamosaic = arcpy.GetParameterAsText(9)

biomassmosaic = arcpy.GetParameterAsText(10)
tcdmosaic30m = arcpy.GetParameterAsText(11)
hansenareamosaic30m = arcpy.GetParameterAsText(12)


overwrite = arcpy.GetParameterAsText(13)

remaptable = os.path.join(os.path.dirname(os.path.abspath(__file__)),"remaptable.dbf")
remapfunction = os.path.join(os.path.dirname(os.path.abspath(__file__)),"remapfunction.rft.xml")
# get user inputs
maindir, shapefile, column_name,main_analysis,biomass_analysis,filename,threshold = user_inputs()

# remap tcd mosaic based on user input
# remapmosaic(threshold,remaptable,remapfunction)

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
def correctfcname(column_name):
    # column_name = unicode(column_name,"ascii","ignore")
    if column_name[0].isdigit():
        column_name = "x"+str(column_name)
    bad = [" ","-",'/', ':', '*', '?', '"', '<', '>', '|']
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
        table_names = {"area only":"area_only","loss and biomass":"area","biomass":"biomass30m","loss":"area"}
        arcpy.AddMessage(overwrite)
        if overwrite == "false":

            if main_analysis != "none":
                analysisfilename = table_names[main_analysis]
                z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + analysisfilename)
                arcpy.AddMessage(z_stats_tbl)
                if not arcpy.Exists(z_stats_tbl):
                    loss_and_biomass(main_analysis)
                else:
                    arcpy.AddMessage(main_analysis + " already exists")
            if biomass_analysis != "none":
                analysisfilename2 = table_names[biomass_analysis]
                z_stats_tbl2 = os.path.join(outdir, column_name2 + "_" + filename + "_" + analysisfilename2)

                if not arcpy.Exists(z_stats_tbl2):
                    biomass30m(biomass_analysis)
                else:
                    arcpy.AddMessage(biomass_analysis + " already exists")
        if overwrite == "true":
            loss_and_biomass(main_analysis)
            biomass30m(biomass_analysis)

        arcpy.AddMessage(  "     " + str(datetime.datetime.now() - fctime))
    del cursor

# merge output fc tables into 1 per analysis
arcpy.AddMessage(  "merge tables")
for option in option_list:
    merge_tables(outdir,option,filename,merged_dir)

# if area was calculated, create area pivot table
# if biomass max exists, then need to average biomass then create biomass pivot table
arcpy.env.workspace = merged_dir
area = arcpy.ListTables(filename+"_area_merge")
if len(area)==1:
    area = arcpy.ListTables(filename+"_area_merge")[0]
    arcpy.AddMessage(  "create loss pivot")
    pivotTable(area,"SUM",filename + "_area_pivot")
    if "biomass_max" in option_list:
        arcpy.AddMessage(  "calc average biomass")
        avgBiomass(merged_dir,column_name,filename)
        arcpy.AddMessage(  "create biomass pivot")
        pivotTable(area,"avgBiomass",filename + "_biomass_pivot")

if "area30m" in option_list:
    area30m = arcpy.ListTables(filename+"_area30m_merge")[0]
    arcpy.AddMessage(  "calc average 30m biomass")
    biomass30m_calcs(merged_dir,column_name,filename)
    arcpy.AddMessage(  "create 30m biomass pivot")
    pivotTable(area30m,"Mgha30m",filename + "_biomass30m_pivot")
    pivotTable(area30m,"SUM",filename + "_area30m_pivot")

if "area_only" in option_list:
    areaonly =arcpy.ListTables(filename+"_area_only_merge")[0]
    arcpy.AddMessage(  "create area only pivot")
    pivotTable(areaonly,"SUM",filename + "_area_only_pivot")

# clean up temp files
arcpy.AddMessage("cleaning up temps")
arcpy.env.workspace = merged_dir
temp = arcpy.ListTables("*merge")
for t in temp:
    arcpy.Delete_management(t)