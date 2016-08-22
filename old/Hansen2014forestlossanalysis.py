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
1. indir- change this to the name of the input zone file
2. area_type- useful for calculating national, subnational, protected areas, etc. A way to distinguish the output tables
3. column name- should be the name of the column in the shapefile that is the unique ID. Values in this column become the output zonal stats table name
4. hansen loss year data mosaic
5. tree cover density mosaic
6. area tiles mosaic
'''

''' Section 1: Set environments ##############################################################################'''
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"
############################################################################################################

''' Section 2: Set directories ##############################################################################'''
indir = r'C:\Users\inputfile.shp'
#------------------------------------
maindir = os.path.abspath(os.getcwd())
outdir = os.path.join(maindir,"outdir")
if not os.path.exists(outdir):
    os.mkdir(outdir)
############################################################################################################

'''Section 3: Set variables for admininstrative level #######################################################'''
area_type = "nat"
column_name = "adm0_id"
#------------------------------------
area_dbf = "_"+area_type + "_area.dbf"
error_text_file = os.path.join(maindir,area_type + '_errors.txt')

'''Section 4: set path to mosaic files #################################################################'''
lossyearmosaic = r'C:\Users\lossdata_2001_2014'
tcdmosaic = r'C:\Users\new_2000_treecover_remap'
hansenareamosaic = r'C:\Users\hansen_area'
############################################################################################################

'''Section 5: Set environments (part 2) #####################################################################'''
scratch_gdb = os.path.join(maindir,"scratch.gdb")
if not os.path.exists(scratch_gdb):
    arcpy.CreateFileGDB_management(maindir,"scratch.gdb")
scratch_workspace = os.path.join(maindir,"scratch.gdb")
arcpy.env.scratchWorkspace = scratch_workspace
arcpy.env.workspace = outdir
arcpy.env.snapRaster = hansenareamosaic
############################################################################################################

'''Section 6: Prepare variables for inside script ############################################################'''
start = datetime.datetime.now()
total_features = arcpy.GetCount_management(indir)
total_features = int(total_features.getOutput(0))
############################################################################################################

'''Section 7: main body of script ############################################################################'''
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
'''                 Section 7a: extract by mask ###############################################################'''
                    print "     extracting by mask"
                    outExtractbyMask = ExtractByMask(lossyearmosaic,fc)
'''                 Section 7b: add loss data to tcd mosaic ###################################################'''
                    print "     adding"
                    outPlus =outExtractbyMask+Raster(tcdmosaic)
'''                 Section 7c: run zonal stats ###############################################################'''
                    arcpy.env.cellSize = "MAXOF"
                    print "     zonal stats area"
                    arcpy.gp.ZonalStatisticsAsTable_sa(outPlus, "VALUE", hansenareamosaic,zonalstats_area, "DATA", "SUM")
'''                 Section 7d: add and calculate an ID field ###################################################'''
                    arcpy.AddField_management(zonalstats_area,"ID","TEXT")
                    arcpy.CalculateField_management(zonalstats_area,"ID","'" + expression + "'","PYTHON_9.3")
                    print "     elapsed time: " + str(datetime.datetime.now() - a)
'''                 Section 7e: cleanup temp rasters ###########################################################'''
                    arcpy.env.workspace = scratch_workspace
                    rasterlist = arcpy.ListRasters()
                    for raster in rasterlist:
                        arcpy.Delete_management(raster)
'''                 Section 7f: error handlers #################################################################'''
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
'''Section 8: compile output tables ##########################################################################'''
arcpy.env.workspace = outdir
print "merging tables"
tablelist_area = arcpy.ListTables("*"+area_dbf)
'''Section 8a: list the output tables ########################################################################'''
# list all tables, used for qc later
tablelist_area_text = open(os.path.join(maindir,area_type +'_tableslist_area.txt'),'w')
for table in tablelist_area:
    tablelist_area_text.write(table + '\n')
tablelist_area_text.close()
'''Section 8b: create directory to store output #############################################################'''
# create directory to store output merged table
merged_dir = os.path.join(maindir,'merged')
if not os.path.exists(merged_dir):
    os.mkdir(merged_dir)
'''Section 8c: merge tables #################################################################################'''
area_merge = os.path.join(merged_dir,area_type +'_area_merge_temp.dbf')
area_merge2 = os.path.join(merged_dir,area_type +'_area_merge.dbf')
arcpy.Merge_management(tablelist_area,area_merge)
'''Section 8d: summarize duplicates #########################################################################'''
# summarize all the duplicate values
arcpy.Statistics_analysis(area_merge,area_merge2,[["SUM","SUM"],["COUNT","SUM"]],["VALUE","ID"])
a = datetime.datetime.now()

print "total elapsed time: " + str(datetime.datetime.now() - start)
print "done"
