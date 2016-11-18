import datetime
import os
import subprocess

import arcpy

from processing import zstats
from processing import directories as dir


def merge_tables(outdir, filename, merged_dir):

    arcpy.env.workspace = outdir
    table_list = arcpy.ListTables("*")
    final_merge_table = os.path.join(merged_dir, filename)

    if len(table_list) > 1:
        arcpy.Merge_management(table_list, final_merge_table)


def simple_zonal_stats(shapefile, maindir, raster):
    arcpy.env.overwriteOutput = "TRUE"
    scratch_gdb, outdir, merged_dir = dir.dirs(maindir)
    nodatamosaic = os.path.join(r'U:\sgibbes\carbon_estimate_calcs\New File Geodatabase.gdb',raster)
    hansenareamosaic = r'U:\sgibbes\carbon_estimate_calcs\New File Geodatabase.gdb\biomass'
    filename = "carbon_esti"
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
                print hansenareamosaic
                print nodatamosaic
                zstats_cmd = os.path.join(scripts_dir, 'zstats_cmd.py')

                outputs = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile,
                                                  column_name2,
                                                  outdir)
                mask = outputs[0]
                extent = outputs[1]


                arcpy.env.snapRaster = nodatamosaic
                arcpy.env.mask = mask
                arcpy.env.extent = extent
                print "zonal stats"
                arcpy.gp.ZonalStatisticsAsTable_sa(nodatamosaic, "VALUE", hansenareamosaic, z_stats_tbl, "DATA", "SUM")
                #
                # cmd = ["C:\Python27\ArcGIS10.4\python.exe", zstats_cmd,
                #        '-v', hansenareamosaic, '-z', nodatamosaic, '-m', mask, '-t', z_stats_tbl]
                #
                # # silence error message
                # FNULL = open(os.devnull, 'w')
                # try:
                #
                #
                #     subprocess.check_call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)
                #
                # except:
                #
                #     print "not running this"


                #
                # zstats.zonal_stats(nodatamosaic, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask,
                #                    scratch_gdb, outdir, column_name2, column_name2, extent)

                print "Elapsed Time: {}".format(str(datetime.datetime.now() - fctime))
            else:
                print "already exists"
    print "Total Run Time: {}".format(str(datetime.datetime.now() - start_time))
    return outdir, filename, merged_dir
rasters_to_process = ['floristic', 'ifl_country', 'ifl_eco_region']

for raster in rasters_to_process:
    print raster
    outfolder_name = raster.split("ifl")[-1].strip("_")
    out_path = os.path.join(r'U:\sgibbes\carbon_estimate_calcs', 'carbon_estimates_' + outfolder_name )
    print out_path
    outdir, filename, merged_dir = simple_zonal_stats(r'U:\sgibbes\carbon_estimate_calcs\remaining_biomass_tiles_overland.shp',
                       out_path, raster)

# merge_tables(outdir, filename, merged_dir)


