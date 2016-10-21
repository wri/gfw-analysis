import arcpy
import datetime

from forestloss_classes import zstats
from forestloss_classes import directories as dir

def simple_zonal_stats(shapefile, maindir):
    arcpy.env.overwriteOutput = "TRUE"
    scratch_gdb, outdir, merged_dir = dir.dirs(maindir)
    nodatamosaic = r'C:\Users\samantha.gibbes\Documents\gis\sample_tiles\mosaics.gdb\nodata'
    hansenareamosaic = r'C:\Users\samantha.gibbes\Documents\gis\sample_tiles\mosaics.gdb\area'
    filename = "areacalcs"
    total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))
    with arcpy.da.SearchCursor(shapefile, ("Shape@", "tmp")) as cursor:
        feature_count = 0

        for row in cursor:
            fc_geo = row[0]
            column_name2 = row[1]

            fctime = datetime.datetime.now()
            feature_count += 1
            arcpy.AddMessage("processing feature {} out of {}".format(feature_count, total_features))
            fc_geo = row[0]

            outputs = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2,
                                              outdir)
            mask = outputs[0]
            extent = outputs[1]

            zstats.zonal_stats(nodatamosaic, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask,
                               scratch_gdb, outdir, column_name2, column_name2, extent)

            print "Elapsed Time: {}".format(str(datetime.datetime.now() - fctime))
simple_zonal_stats(r'C:\Users\samantha.gibbes\Documents\gis\land_area_calcs\adm1_to_test.shp',
                   r'C:\Users\samantha.gibbes\Documents\gis\land_area_calcs')
