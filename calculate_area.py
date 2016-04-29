__author__ = 'sgibbes'
import arcpy
import os

# get user inputs (area from stats is optional)
shapefile = arcpy.GetParameterAsText(0)
area_from_stats = arcpy.GetParameterAsText(1)

arcpy.env.overwriteOutput = "True"
outdir = os.path.dirname(shapefile)
proj_name = os.path.basename(shapefile).split(".")[0]+"_proj"

# create geodatabase to store the projected file
gdb_name = "scratch.gdb"
arcpy.CreateFileGDB_management(outdir, gdb_name)
gdb = os.path.join(outdir,gdb_name)
outproj = os.path.join(gdb,proj_name)

dissolve_name = os.path.basename(shapefile).split(".")[0]+"_diss"
outdissolve = os.path.join(gdb,dissolve_name)

# dissolve the input shapefile to get 1 feature
arcpy.Dissolve_management(shapefile,outdissolve)

# project into equal area projection that works globally
arcpy.Project_management(outdissolve, outproj,
                         out_coor_system="PROJCS['World_Eckert_VI',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],"
                                         "UNIT['Degree',0.0174532925199433]],PROJECTION['Eckert_VI'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],"
                                         "UNIT['Meter',1.0]]", transform_method="", in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],"
                                                                                                   "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", preserve_shape="NO_PRESERVE_SHAPE",max_deviation="")
with arcpy.da.SearchCursor(outproj, ("Shape_Area")) as cursor:
    for row in cursor:
        area = row[0]
arcpy.AddMessage("Area (m2):  %s" % area)
if len(area_from_stats)> 0:
    diff = ((int(area)-int(area_from_stats))/area)*100
    # print "percent diff:  %s" % diff
    arcpy.AddMessage("Percent Difference:  %s" % diff)