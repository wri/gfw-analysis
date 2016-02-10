__author__ = 'sgibbes'
import os
import arcpy
from arcpy import *
from arcpy.sa import *
import time, subprocess
from sys import argv
from boundary_prep_arcpro import *
from dictionaries import dict

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

    z_stats_tbl = os.path.join(outdir, fc_name + "_" + filename + "_" + calculation + ".dbf")

    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + expr + "'", "PYTHON_9.3")
    if not calculation in option_list:
        option_list.append(calculation)


def merge_tables(envir,option,filename,merged_dir):
    arcpy.env.workspace = envir
    table_list = arcpy.ListTables("*_"+option+".dbf")
    arcpy.AddMessage(table_list)
    final_merge_table = os.path.join(merged_dir,filename+"_"+option+'_merge.dbf')
    pivottable = os.path.join(merged_dir,filename+"_"+option+'_merge_pivot.dbf')
    arcpy.Merge_management(table_list,final_merge_table)
    arcpy.management.PivotTable(final_merge_table, "ID", "Value", "SUM", pivottable)
    arcpy.AddField_management(pivottable, "total", "LONG")
    fc = pivottable

    # making a list of fields that contain VSG_EIZEL
    # ex VSG_EINZEL, VSG_EIZEL_1, VSG_EIZEL_2
    field_prefix = "Value"
    field_list = []
    f_list = arcpy.ListFields(fc)
    for f in f_list:
        if field_prefix in f.name:
            if not "Value0" in f.name:
                field_list.append(f.name)
    # use update cursor to find values
    # and update the total field
    rows = arcpy.UpdateCursor(fc)
    for row in rows:
        VSG_SUM = 0
        for f in field_list:
            VSG_SUM += row.getValue(f)
        row.total = VSG_SUM
        rows.updateRow(row)
        del VSG_SUM
    del rows

def loss_and_biomass(option):
    arcpy.env.scratchWorkspace = scratch_gdb
    table_names_27m = ["area","biomass_max","biomass_min"]
    z_stats_tbl = os.path.join(outdir, fc_name + "_" + filename + "_" + table_names_27m[0] + ".dbf")
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



    return maindir, shapefile,column_name,main_analysis,biomass_analysis,filename

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
hansenareamosaic = arcpy.GetParameterAsText(7)
biomassmosaic = arcpy.GetParameterAsText(8)
tcdmosaic30m = arcpy.GetParameterAsText(9)
hansenareamosaic30m = arcpy.GetParameterAsText(10)
lossyearmosaic = arcpy.GetParameterAsText(11)
tcdmosaic = arcpy.GetParameterAsText(12)
maindir, shapefile, column_name,main_analysis,biomass_analysis,filename = user_inputs()

arcpy.env.workspace = maindir
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"
scratch_gdb = os.path.join(maindir, "scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir, "scratch.gdb")
arcpy.env.scratchWorkspace = scratch_gdb
error_text_file = os.path.join(maindir,'errors.txt')
outdir = os.path.join(maindir, "outdir")
if not os.path.exists(outdir):
    os.mkdir(outdir)
merged_dir = os.path.join(maindir,'merged')
if not os.path.exists(merged_dir):
    os.mkdir(merged_dir)


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
arcpy.AddMessage(  "merge tables")
for option in option_list:
    merge_tables(outdir,option,filename,merged_dir)

arcpy.AddMessage(  "\n total elapsed time: " + str(datetime.datetime.now() - start))
