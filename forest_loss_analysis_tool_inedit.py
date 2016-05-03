__author__ = 'sgibbes'
import os
import arcpy
from arcpy import *
from arcpy.sa import *
import time, subprocess
from sys import argv
from boundary_prep_arcpro import *
from dictionaries import dict

def zonal_stats_forest(zone_raster, value_raster, area_type, calculation, snapraster):
    arcpy.AddMessage(  "zonal stats")
    arcpy.env.snapRaster = snapraster
    if calculation == "biomass_max" or calculation == "area"or calculation == "area_only":
        arcpy.env.cellSize = "MAXOF"
    if calculation == "biomass_min":
        arcpy.env.cellSize = "MINOF"
    if calculation == "area_30m" or calculation == "biomass_30m":
        arcpy.env.cellSize = "MAXOF"
    expr = fc_name.split("_")[0]
    z_stats_tbl = os.path.join(outdir, fc_name + "_" + area_type + "_" + calculation + ".dbf")
    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + expr + "'", "PYTHON_9.3")
    if not calculation in option_list:
        option_list.append(calculation)

def merge_tables(envir,dbf_name,area_type,boundary_id,merged_dir):
    arcpy.env.workspace = envir
    table_list = arcpy.ListTables("*_"+dbf_name+".dbf*")
    temp_merge_table = os.path.join(merged_dir,str(boundary_id) + "_"+area_type +"_"+dbf_name + '_temp.dbf')
    final_merge_table = os.path.join(merged_dir,str(boundary_id) + "_"+area_type +"_"+dbf_name + '_merge.dbf')
    arcpy.Merge_management(table_list,temp_merge_table)
    arcpy.Statistics_analysis(temp_merge_table,final_merge_table,[["SUM","SUM"],["COUNT","SUM"]],["VALUE","ID"])
    arcpy.AddField_management(final_merge_table, "boundary", "TEXT")
    arcpy.CalculateField_management(final_merge_table, "boundary", "'" + boundary_id + "'", "PYTHON_9.3")
    outtable = str(boundary_id) + "_"+area_type +"_"+dbf_name + '_merge.txt'
    arcpy.TableToTable_conversion(final_merge_table,merged_dir,outtable)
def forest_loss():
    arcpy.AddMessage("extracting for forest loss")
    lossyr_tcd = ExtractByMask(lossyearmosaic, fc_geo) + Raster(tcdmosaic)
    table = table_names_27m[0]
    zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename, table, hansenareamosaic, column_name)
    if not table in option_list:
        option_list.append(table)
    del lossyr_tcd
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
maindir, shapefile, column_name,analysis_choice,biomass_analysis,filename,threshold = user_inputs()
if threshold != "all":
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


if option_list[0] == "true":
    function = "forest_loss()"
print function

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


        if analysis_choice != "none":
            analysisfilename = table_names[analysis_choice]
            z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + analysisfilename)
            arcpy.AddMessage(z_stats_tbl)
            if not arcpy.Exists(z_stats_tbl):
                function
            else:
                arcpy.AddMessage(analysis_choice + " already exists")

        if overwrite == "true":
            analysis(analysis_choice)

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
arcpy.Delete_management(outdir)
arcpy.Delete_management(scratch_gdb)
