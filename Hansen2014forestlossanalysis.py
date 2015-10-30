# Section 1
import os
import arcpy
from arcpy.sa import *
import time, subprocess

'''
author: Sam Gibbes
Date: 10/29/15

pre processing:
1. if any aoi features are large,intersect the feature with the data footprint
2. open the attribute table and create a unique id column, name it adm0_id
3. Calculate the unique id column to be python syntax, !ISO! + "_" + str(!FID!)

Paths/names to change in script:
1. line 30: indir- change this to the name of the input zone file
2. line 37: area_type- useful for calculating national, subnational, protected areas, etc. A way to distinguish the output tables
3. line 38: column name- should be the name of the column in the shapefile that is the unique ID. Values in this column become the output zonal stats table name
4. line 43: hansen loss year data mosaic
5. line 44: tree cover density mosaic
6. line 45: area tiles mosaic
'''
# set environments, pt1
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

# directories and variables
maindir = os.path.abspath(os.getcwd())
indir = r'C:\Users\inputfile.shp'
outdir = os.path.join(maindir,"outdir")
if not os.path.exists(outdir):
    os.mkdir(outdir)

# this builds the suffix for the output file. useful for running more than just area stats (biomass)
# ex: BRA_1 -> BRA_1_nat_area.dbf
area_type = "nat"
column_name = "adm0_id"
area_dbf = "_"+area_type + "_area.dbf"

error_text_file = os.path.join(maindir,area_type + '_errors.txt')

lossyearmosaic = r'C:\Users\lossdata_2001_2014'
tcdmosaic = r'C:\Users\new_2000_treecover_remap'
hansenareamosaic = r'C:\Users\hansen_area'

# set environments, pt2
scratch_gdb = os.path.join(maindir,"scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir,"scratch.gdb")
scratch_workspace = os.path.join(maindir,"scratch.gdb")
arcpy.env.scratchWorkspace = scratch_workspace
arcpy.env.workspace = outdir
arcpy.env.snapRaster = hansenareamosaic

start = datetime.datetime.now()
total_features = arcpy.GetCount_management(indir)
total_features = int(total_features.getOutput(0))

with arcpy.da.SearchCursor(indir,("Shape@",column_name)) as cursor:
    feature_count = 0
    for row in cursor:
        feature_count += 1
        fc = row[0]
        value = str(row[1])
        expression = value.split("_")[0]
        iso = value[:3]
        list = ['']
        if iso in list:
            pass
        else:
            zonalstats_area = os.path.join(outdir,value + area_dbf)
            if not os.path.exists(zonalstats_area):
                print "\n" + value + " " + str(feature_count)+"/"+str(total_features)
                a = datetime.datetime.now()

                try:
                    print "     extracting by mask"
                    outExtractbyMask = ExtractByMask(lossyearmosaic,fc)
                    print "     adding"
                    outPlus =outExtractbyMask+Raster(tcdmosaic)
                    arcpy.env.cellSize = "MAXOF"
                    print "     zonal stats area"
                    arcpy.gp.ZonalStatisticsAsTable_sa(outPlus, "VALUE", hansenareamosaic,zonalstats_area, "DATA", "SUM")
                    arcpy.AddField_management(zonalstats_area,"ID","TEXT")
                    arcpy.CalculateField_management(zonalstats_area,"ID","'" + expression + "'","PYTHON_9.3")
                    print "     elapsed time: " + str(datetime.datetime.now() - a)
                    arcpy.env.workspace = scratch_workspace
                    rasterlist = arcpy.ListRasters()
                    for raster in rasterlist:
                        arcpy.Delete_management(raster)

                except IOError as e:
                    print "     failed"
                    error_text = "I/O error({0}): {1}".format(e.errno, e.strerror)
                    errortext = open(error_text_file,'a')
                    errortext.write(value + " " + str(error_text) + "\n")
                    errortext.close()
                    pass
                except ValueError:
                    print "     failed"
                    error_text="Could not convert data to an integer."
                    errortext = open(error_text_file,'a')
                    errortext.write(value + " " + str(error_text) + "\n")
                    errortext.close()
                    pass
                except:
                    print "     failed"
                    error_text= "Unexpected error:", sys.exc_info()
                    error_text= error_text[1][1]
                    errortext = open(error_text_file,'a')
                    errortext.write(value + " " + str(error_text) + "\n")
                    errortext.close()
                    pass
            else:
                print value + " already exists"

arcpy.env.workspace = outdir
print "merging tables"
tablelist_area = arcpy.ListTables("*"+area_dbf)

# list all tables, used for qc later
tablelist_area_text = open(os.path.join(maindir,area_type +'_tableslist_area.txt'),'w')
for table in tablelist_area:
    tablelist_area_text.write(table + '\n')
tablelist_area_text.close()

# create directory to store output merged tables
merged_dir = os.path.join(maindir,'merged')
if not os.path.exists(merged_dir):
    os.mkdir(merged_dir)

area_merge = os.path.join(merged_dir,area_type +'_area_merge_temp.dbf')
area_merge2 = os.path.join(merged_dir,area_type +'_area_merge.dbf')
arcpy.Merge_management(tablelist_area,area_merge)

# summarize all the duplicate values
arcpy.Statistics_analysis(area_merge,area_merge2,[["SUM","SUM"],["COUNT","SUM"]],["VALUE","ID"])
a = datetime.datetime.now()

print "total elapsed time: " + str(datetime.datetime.now() - start)
print "done"
