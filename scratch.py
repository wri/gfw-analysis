__author__ = 'sgibbes'
import os
from arcpy import *
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

def avgBiomass(merged_dir,filename):
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
def boundary_prep(fc,outdir,analysis_boundary,column_name,admin_file,grid,column_calc):
    arcpy.env.overwriteOutput = "TRUE"
    fname = os.path.basename(fc).split(".")[0]
    # check coordinat system
    desc = arcpy.Describe(fc)
    sr = desc.spatialReference
    coords = sr.Name
    if not coords == "GCS_WGS_1984":
        arcpy.AddMessage("projecting feature")
        out_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.Project_management(fc,os.path.join(outdir,fname+"_proj.shp"),out_coor_system)
        fc = os.path.join(outdir,fname+"_proj.shp")
    intersect = os.path.join(outdir,fname+"_intersect.shp")
    if analysis_boundary == "land use boundary":
        arcpy.Dissolve_management(fc,"in_memory/dissolve")
        arcpy.AddMessage("intersecting feature, land use boundary")
        arcpy.Intersect_analysis(["in_memory/dissolve",admin_file],"in_memory/intersect")
        arcpy.Intersect_analysis(["in_memory/intersect",grid],intersect)
        arcpy.AddField_management(intersect,column_name,"TEXT","","",15)
        arcpy.CalculateField_management(intersect, column_name,column_calc ,"PYTHON_9.3")
    if analysis_boundary == "country level":
        arcpy.AddMessage("intersecting feature, country boundary")
        arcpy.Intersect_analysis([fc,grid],intersect)
        arcpy.AddField_management(intersect,column_name,"TEXT","","",15)
        arcpy.CalculateField_management(intersect, column_name,column_calc ,"PYTHON_9.3")
    # project
    # calculate area
    # if area <
    return intersect
def dict(admin_level,adm0,adm1,adm2):
    admin_level_dict = {'national':adm0,'subnational':adm1,'district':adm2}
    column_name_dict = {'national':'adm0_id','subnational':'adm1_id','district':'adm2_id'}
    area_type_dict = {'national':'nat','subnational':'subnat','district':'dist'}
    column_calc_dict = {'national':"""!ISO!+"_"+ str(!FID!)""",'subnational':"""!ISO!+str( !ID_1!)+"_"+ str(!FID!)""",'district':"""!ISO!+"d"+str( !ID_2!)+"_"+ str(!FID!)"""}
    return column_name_dict[admin_level],column_calc_dict[admin_level], area_type_dict[admin_level], admin_level_dict[admin_level]
def correctfcname(column_name):
    # replaced bad characters in table field
    if column_name[0].isdigit():
        column_name = "x"+str(column_name)
    bad = [" ","-",'/', ':', '*', '?', '"', '<', '>', '|','.']
    for char in bad:
        column_name = column_name.replace(char,"_")
    return  column_name
def zonal_stats_forest(zone_raster, value_raster, filename, calculation, snapraster):
    arcpy.AddMessage(  "zonal stats")
    arcpy.env.snapRaster = snapraster
    if calculation == "biomass_max" or calculation == "area"or calculation == "area_only":
        arcpy.env.cellSize = "MAXOF"
    if calculation == "biomass_min":
        arcpy.env.cellSize = "MINOF"
    if calculation == "area_30m" or calculation == "biomass_30m":
        arcpy.env.cellSize = "MAXOF"
    z_stats_tbl = os.path.join(outdir, c + "_" + filename + "_" + calculation)
    arcpy.gp.ZonalStatisticsAsTable_sa(zone_raster, "VALUE", value_raster, z_stats_tbl, "DATA", "SUM")
    return z_stats_tbl
def calculatefield(z_stats_tbl,c):
    arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
    expr = c.split("_")[0]
    arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + expr + "'", "PYTHON_9.3")

maindir = r'D:\_sam\scratch'
shapefile = r'D:\_sam\scratch\shapefile_sub.shp'
filename = "test"
analysis_boundary = "country level"
admin_level= "subnational"
main_analysis= "loss and biomass"
biomass_analysis = "none"
lossyearmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\lossdata_2001_2014'
tcdmosaic = r'H:\gfw_gis_team_data\mosaics.gdb\treecoverdensity_2000'
hansenareamosaic = r'H:\gfw_gis_team_data\mosaics.gdb\hansen_area'
adm0 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm0'
adm1 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm1'
adm2 = r'H:\gfw_gis_team_data\gadm27_levels.gdb\adm2'
grid = r'H:\gfw_gis_team_data\lossdata_footprint.shp'

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

column_name,column_calc, area_type,admin_file = dict(admin_level,adm0,adm1,adm2)
boundary = boundary_prep(shapefile,maindir,analysis_boundary,column_name,admin_file,grid,column_calc)
table_names = {"area only":"area_only","loss and biomass":"area","biomass":"biomass30m","loss":"area"}

table = table_names[main_analysis]
with arcpy.da.SearchCursor(boundary, ("Shape@", column_name)) as cursor:
    feature_count = 0
    for row in cursor:
        fctime = datetime.datetime.now()
        feature_count += 1
        fc_geo = row[0]
        c = row[1]
        lossyr_tcd = ExtractByMask(lossyearmosaic,fc_geo) + Raster(tcdmosaic)
        z_stats_tbl=zonal_stats_forest(lossyr_tcd, hansenareamosaic, filename,table,hansenareamosaic)
        calculatefield(z_stats_tbl,c)
        avgBiomass(merged_dir,filename)
        arcpy.AddMessage(  "     " + str(datetime.datetime.now() - fctime))
    del cursor