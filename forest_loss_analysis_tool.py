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

def loss_and_biomass(option):
    arcpy.env.scratchWorkspace = scratch_gdb
    table_names_27m = ["area","biomass_max","biomass_min"]
    z_stats_tbl = os.path.join(outdir, fc_name + "_" + area_type + "_" + table_names_27m[0] + ".dbf")
    if option != "None":
        if not os.path.exists(z_stats_tbl):
            arcpy.env.snapRaster = hansenareamosaic
            arcpy.AddMessage(  "extracting")
            lossyr_tcd = ExtractByMask(lossyearmosaic,fc_geo) + Raster(tcdmosaic)
            try:
                if option == "loss":
                    table = table_names_27m[0]
                    zonal_stats_forest(lossyr_tcd, hansenareamosaic, area_type,table,hansenareamosaic)
                    if not table in option_list:
                        option_list.append(table)
                if option == "loss and biomass":
                    zonal_stats_forest(lossyr_tcd, hansenareamosaic, area_type,table_names_27m[0],hansenareamosaic)
                    zonal_stats_forest(lossyr_tcd, biomassmosaic, area_type,table_names_27m[1],hansenareamosaic)
                    zonal_stats_forest(lossyr_tcd, biomassmosaic, area_type,table_names_27m[2],hansenareamosaic)
                    if not table_names_27m[0] in option_list:
                        option_list.extend(table_names_27m)
                if option == "area only":
                    table = "area_only"
                    arcpy.env.snapRaster = hansenareamosaic
                    zoneraster = ExtractByMask(input_zone,fc_geo)
                    zonal_stats_forest(zoneraster, hansenareamosaic, area_type,table,hansenareamosaic)
                    if not "area_only" in option_list:
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
        zonal_stats_forest(tcdmosaic30m, area_extract, area_type, "area30m",hansenareamosaic30m)
        zonal_stats_forest(tcdmosaic30m, outPlus, area_type, "biomass30m",hansenareamosaic30m)
        if not "area30m" in option_list:
            option_list.extend(["area30m","biomass30m"])
        time = str(datetime.datetime.now() - start)
    if option == "none":
        pass
    return option_list

def user_inputs():
    maindir = arcpy.GetParameterAsText(0)
    boundary = arcpy.GetParameterAsText(1)
    boundary_id = arcpy.GetParameterAsText(2)
    main_analysis= arcpy.GetParameterAsText(3)
    biomass_analysis = arcpy.GetParameterAsText(5)
    analysis_boundary  = arcpy.GetParameterAsText(9) # land use boundary or country level
    if main_analysis == "area only":
        input_zone = arcpy.GetParameterAsText(4)
    admin_level = arcpy.GetParameterAsText(6)
    column_name,column_calc, area_type,admin_file = dict(admin_level,adm0,adm1,adm2)

    if admin_level == "other":
        area_type = arcpy.GetParameterAsText(7) # "You want to run a custom area. Enter a short name to give your area (less than 15 characters):
        column_name = arcpy.GetParameterAsText(8) #Enter the name of the column which uniquely identifies each feature in the input shapefile

    return maindir, boundary, area_type,column_name,main_analysis,biomass_analysis,boundary_id,analysis_boundary,admin_level,column_calc,admin_file
#--------------------------

# set input files
hansenareamosaic = r'H:\gfw_gis_team_data\mosaics.gdb\hansen_area'
biomassmosaic = r'H:\gfw_gis_team_data\whrc_carbon\whrc_carbon.gdb\whrc_carbon'
tcdmosaic30m = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_30m_2000'
hansenareamosaic30m = r'H:\gfw_gis_team_data\mosaics.gdb\hansen_area_30m'
lossyearmosaic = r'D:\_sam\mosaics.gdb\lossdata_2001_2014_remp'
tcdmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_2010'
# tcdmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_2010'
adm0 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm0'
adm1 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm1'
adm2 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm2'
grid = r'H:\gfw_gis_team_data\lossdata_footprint.shp'

maindir, boundary1, area_type,column_name,main_analysis,biomass_analysis,boundary_id,analysis_boundary,admin_level,column_calc,admin_file = user_inputs()

arcpy.env.workspace = maindir
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"
scratch_gdb = os.path.join(maindir, "scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir, "scratch.gdb")
arcpy.env.scratchWorkspace = scratch_gdb
error_text_file = os.path.join(maindir,area_type + '_errors.txt')
outdir = os.path.join(maindir, "outdir")
if not os.path.exists(outdir):
    os.mkdir(outdir)
merged_dir = os.path.join(maindir,'merged')
if not os.path.exists(merged_dir):
    os.mkdir(merged_dir)

boundary = boundary_prep(boundary1,maindir,analysis_boundary,column_name,admin_file,grid,column_calc)
total_features = int(arcpy.GetCount_management(boundary).getOutput(0))
start = datetime.datetime.now()
option_list = []
with arcpy.da.SearchCursor(boundary, ("Shape@", column_name)) as cursor:
    feature_count = 0
    for row in cursor:
        fctime = datetime.datetime.now()
        feature_count += 1
        fc_geo = row[0]
        fc_name = str(row[1])
        arcpy.AddMessage( fc_name + " " + str(feature_count)+"/"+str(total_features))
        loss_and_biomass(main_analysis)
        biomass30m(biomass_analysis)
        arcpy.AddMessage(  "     " + str(datetime.datetime.now() - fctime))
    del cursor

arcpy.AddMessage(  "merge tables")
for option in option_list:
    merge_tables(outdir,option,area_type,boundary_id,merged_dir)
arcpy.AddMessage(  "clean up temps")
arcpy.env.workspace=merged_dir
delete_tables = arcpy.ListTables("*temp*")
for d in delete_tables:
    arcpy.Delete_management(d)
arcpy.AddMessage(  "\n total elapsed time: " + str(datetime.datetime.now() - start))
