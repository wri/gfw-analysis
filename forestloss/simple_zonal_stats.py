import arcpy
import datetime
import os

from forestloss_classes import zstats
from forestloss_classes import directories as dir

def merge_tables(outdir, filename, merged_dir):

    arcpy.env.workspace = outdir
    table_list = arcpy.ListTables("*")
    final_merge_table = os.path.join(merged_dir, filename)

    if len(table_list) > 1:
        arcpy.Merge_management(table_list, final_merge_table)


def simple_zonal_stats(shapefile, maindir):
    arcpy.env.overwriteOutput = "TRUE"
    scratch_gdb, outdir, merged_dir = dir.dirs(maindir)
    zone_mosaic = r'C:/Users/samantha.gibbes/Documents/gis/carbon_storage_estimates/New File Geodatabase.gdb/ifl_country'
    value_mosaic = r'C:/Users/samantha.gibbes/Documents/gis/carbon_storage_estimates/New File Geodatabase.gdb/biomass'
    filename = "areacalcs"
    total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))
    with arcpy.da.SearchCursor(shapefile, ("Shape@", "FC_NAME")) as cursor:
        feature_count = 0

        for row in cursor:
            column_name2 = row[1]

            fctime = datetime.datetime.now()
            feature_count += 1
            arcpy.AddMessage("processing feature {} out of {}".format(feature_count, total_features))
            fc_geo = row[0]

            outputs = zstats.zonal_stats_mask(value_mosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2,
                                              outdir)
            mask = outputs[0]
            extent = outputs[1]

            zstats.zonal_stats(zone_mosaic, value_mosaic, filename, "forest_loss", value_mosaic, mask,
                               scratch_gdb, outdir, column_name2, column_name2, extent)

            print "Elapsed Time: {}".format(str(datetime.datetime.now() - fctime))

    return outdir, filename, merged_dir

outdir, filename, merged_dir = simple_zonal_stats(r'C:\Users\samantha.gibbes\Documents\gis\carbon_storage_estimates\test\test_grid.shp',
                   r'C:\Users\samantha.gibbes\Documents\gis\carbon_storage_estimates\test')

# merge_tables(outdir, filename, merged_dir)
