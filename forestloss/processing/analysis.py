import arcpy

import zstats as zstats

arcpy.env.overwriteOutput = True

def forest_loss_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname):
    outputs = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    mask = outputs[0]
    extent = outputs[1]
    zstats.zonal_stats(lossyr, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname, extent)


def carbon_emissions_function(hansenareamosaic,biomassmosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname):
    outputs = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    mask = outputs[0]
    extent = outputs[1]

    zstats.zonal_stats(lossyr, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask, maindir, outdir,
                       column_name2, orig_fcname, extent)
    zstats.zonal_stats(lossyr, biomassmosaic, filename, "emissions", hansenareamosaic, mask, maindir, outdir,
                       column_name2, orig_fcname, extent)


def biomass_weight_function(hansenareamosaic, biomassmosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2,
                            outdir, tcdmosaic, filename, orig_fcname):
    outputs = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    mask = outputs[0]
    extent = outputs[1]
    zstats.zonal_stats(tcdmosaic, biomassmosaic, filename, "biomassweight", hansenareamosaic, mask, scratch_gdb,
                       outdir, column_name2, orig_fcname, extent)


def tree_cover_extent_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,tcdmosaic,filename,orig_fcname):
    outputs = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    mask = outputs[0]
    extent = outputs[1]
    zstats.zonal_stats(tcdmosaic, hansenareamosaic, filename, "tree_cover_extent", hansenareamosaic, mask, scratch_gdb,
                       outdir, column_name2, orig_fcname, extent)

# shapefile = r'U:\sgibbes\GitHub\gfw-analysis\forestloss\test_4pix.shp'
# maindir = r'U:\sgibbes\test\test_mon'
# import directories as dir
# scratch_gdb, outdir, merged_dir = dir.dirs(maindir)
# with arcpy.da.SearchCursor(shapefile, ("Shape@", "FC_NAME")) as cursor:
#     feature_count = 0
#     for row in cursor:
#
#         feature_count += 1
#
#         fc_geo = row[0]
#         column_name2 = row[1]
#         orig_fcname = "FID"
#         filename = "test"
#         hansenareamosaic = r'U:\sgibbes\New File Geodatabase.gdb\area'
#         biomassmosaic = r'U:\sgibbes\New File Geodatabase.gdb\biomass'
#         tcdmosaic = r'U:\sgibbes\New File Geodatabase.gdb\tcd'
#         biomass_weight_function(hansenareamosaic, biomassmosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2,
#                                 outdir, tcdmosaic, filename, orig_fcname)