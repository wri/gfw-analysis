import datetime
import os
import subprocess

import arcpy

from forestloss_classes import zstats
from processing import directories as dir


def merge_tables(outdir, filename, merged_dir):

    arcpy.env.workspace = outdir
    table_list = arcpy.ListTables("*")
    final_merge_table = os.path.join(merged_dir, filename)

    if len(table_list) > 1:
        arcpy.Merge_management(table_list, final_merge_table)


def simple_zonal_stats(shapefile, maindir):
    arcpy.env.overwriteOutput = "TRUE"
    scratch_gdb, outdir, merged_dir = dir.dirs(maindir)
    nodatamosaic = r'U:\sgibbes\New File Geodatabase.gdb\nodata'
    hansenareamosaic = r'U:\sgibbes\New File Geodatabase.gdb\area'
    filename = "areacalcs"
    total_features = int(arcpy.GetCount_management(shapefile).getOutput(0))
    start_time = datetime.datetime.now()
    with arcpy.da.SearchCursor(shapefile, ("Shape@", "FC_NAME")) as cursor:
        feature_count = 0

        for row in cursor:
            fc_geo = row[0]
            column_name2 = row[1]

            fctime = datetime.datetime.now()
            feature_count += 1
            arcpy.AddMessage("processing feature {} out of {}".format(feature_count, total_features))
            fc_geo = row[0]
            z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_forest_loss")
            this_dir = os.path.dirname(os.path.abspath(__file__))
            scripts_dir = os.path.join(this_dir, "forestloss_classes")
            if not arcpy.Exists(z_stats_tbl):

                zstats_cmd = os.path.join(scripts_dir, 'zstats_cmd.py')

                outputs = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile,
                                                  column_name2,
                                                  outdir)
                mask = outputs[0]
                extent = outputs[1]

                cmd = ["C:\Python27\ArcGIS10.4\python.exe", zstats_cmd,
                       '-v', hansenareamosaic, '-z', nodatamosaic, '-m', mask, '-t', z_stats_tbl]

                # silence error message
                FNULL = open(os.devnull, 'w')
                try:


                    subprocess.check_call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)

                except:

                    print "not running this"


                #
                # zstats.zonal_stats(nodatamosaic, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask,
                #                    scratch_gdb, outdir, column_name2, column_name2, extent)

                print "Elapsed Time: {}".format(str(datetime.datetime.now() - fctime))
            else:
                print "already exists"
    print "Total Run Time: {}".format(str(datetime.datetime.now() - start_time))
    return outdir, filename, merged_dir

outdir, filename, merged_dir = simple_zonal_stats(r'U:\sgibbes\tropics_adm0_clippedtocarbon_proj_int_carbon_proj.shp',
                   r'U:\sgibbes\land_area_calcs')

merge_tables(outdir, filename, merged_dir)


